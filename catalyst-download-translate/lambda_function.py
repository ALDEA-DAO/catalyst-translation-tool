import requests
import json
import sqlalchemy
from sqlalchemy import create_engine
import pandas as pd
from io import StringIO
from tqdm import tqdm
import os
import sys
from os import environ

from google.cloud import translate

import textwrap
import random

#Hay un límite de caracteres a traducir por llamada API 
maxChars = 30720

#Levanto las variables desde el archivo de settings
from settings import credential,campaignsColumns , ideasColumns,columnas_traducirCampaings , columnas_traducirCampaignsJSON , columnas_traducirIdeas,columnas_traducirIdeasJSON ,urlAPI,campaignsColumnsTipos,ideasColumnsTipos

def lambda_handler(event, context):
	 
	engine = create_engine('postgresql://'+credential['username']+':'+credential['password']+'@'+credential['host']+':5432/' + credential['db'])
	
	connection = engine.raw_connection()

	cursor = connection.cursor()
	query = "SELECT version() AS version"
	cursor.execute(query)
	results = cursor.fetchone()
	cursor.close()

	print( results[0])
	 
	action = event['action']
	dbname = event['dbname']
	
	tablename_campaigns = "campaigns_" + dbname
	tablename_ideas = "ideas_" + dbname

	tablename_campaigns_esp = "campaigns_esp_" + dbname
	tablename_ideas_esp = "ideas_esp_" + dbname

	print( action)


	if action == "setMostrarTabla":

		print("setMostrarTabla")

		nombreProyecto = event['nombreProyecto']
		cursor = connection.cursor()
		cursor.execute('UPDATE "mostrarTabla" SET nombre = \'%s\',"nombreSQL" = \'%s\'   WHERE id = 1'%(nombreProyecto,dbname))
		connection.commit()

		print("setMostrarTabla - OK")

		return {
			'statusCode': 200,
			'swSetMostrarTabla': True
		}

	elif action == "download":

		print("Downloading Campaings and Ideas")

		URL = urlAPI + "campaigns/active"
		Headers = { 'api_token' : credential['ideaScale API Token'] }
		campaignsText = requests.get(URL, headers=Headers)
		campaigns =pd.read_json(StringIO(campaignsText.text),dtype = False)

		if len(campaigns)>0:

			#clean convierte los campos tipo list, series y dict en str 			
			campaigns = clean(campaigns)

			#revisarCampos inicializa campos que no esten en el dataframe en funcion del tipo
         #a veces el api de ideascale trae diferencias en los campos de acuerdo a cuales campanas e ideas trae
         #de esta forma unifico todo para guardar en la base de datos			
			campaigns = revisarCampos(campaigns,campaignsColumnsTipos)

			cursor = connection.cursor()
			cursor.execute("DROP TABLE IF EXISTS %s;"%tablename_campaigns )
			cursor.execute("DROP TABLE IF EXISTS %s;"%tablename_ideas )
			connection.commit()

			#este campo esta creado para que luego a mano tenga que editarlo y poner la imagen. por ahora copia la misma imagen que logo
         #y actualizo este campo de forma manual luego en la base de datos
			campaigns ["featureImage"] = campaigns ["logoImage"] 

			#NO PUDE SCRAPEAR ese campo desde la página de Catalyst en Ideascale... tiene segurodad cloudflare que no pude pasar....
         
			#headers = {'User-Agent': 'Mozilla/5.0 (iPod; CPU iPhone OS 12_0 like macOS) AppleWebKit/602.1.50 (KHTML, like Gecko) Version/12.0 Mobile/14A5335d Safari/602.1.50'}
			#https://cardano.ideascale.com/a/campaign-home/26433
			#for index, campaign in campaigns.iterrows():
			#	urlCampaign = urlCampaigns.replace("[CAMPAIGN_ID]",str(campaign["id"]))
			#	page = requests.get(urlCampaign, headers=headers)
			#	soup = BeautifulSoup(page.content, "html.parser")
			#	divImagen = soup.find_all("div", class_="col-sm col-md-5 CampaignDetails_featureImage__TORb")

			#	ua = UserAgent()
			#	print(ua.chrome)
			#	header = {'User-Agent':str(ua.chrome)}
			#	print(header)
			#	url = "https://www.hybrid-analysis.com/recent-submissions?filter=file&sort=^timestamp"
			#	htmlContent = requests.get(url, headers=header)

			#	for div in divImagen:
			#		img_element = divImagen.find("img")
			#		campaign["featureImage"]  = img_element.src

			#guardo en la base de datos
			campaigns.to_sql (name=tablename_campaigns, con=engine, if_exists='append', index = False)

			print("Download Campaings OK")

			for i in range(len(campaigns)):

				#solicito al api las ideas de la página 0
				page = 0
				cant = 50

				URL = urlAPI + "campaigns/%s/ideas/%s/%s"%(campaigns['id'].iloc[i],page,cant)
				Headers = { 'api_token' : credential['ideaScale API Token'] }
				ideasText = requests.get(URL, headers=Headers)
				ideas =pd.read_json(StringIO(ideasText.text),dtype = False)
		
				while (len(ideas)>0):
					
					#clean convierte los campos tipo list, series y dict en str 
					ideas = clean(ideas)

					#revisarCampos inicializa campos que no esten en el dataframe en funcion del tipo
					#a veces el api de ideascale trae diferencias en los campos de acuerdo a cuales campanas e ideas trae
					#de esta forma unifico todo para guardar en la base de datos	
					ideas = revisarCampos(ideas,ideasColumnsTipos)

					#guardo en la base de datos
					ideas.to_sql (name=tablename_ideas, con=engine, if_exists='append', index = False)

					#solicito al api las ideas de una nueva página
					page += 1

					URL = urlAPI + "campaigns/%s/ideas/%s/%s"%(campaigns['id'].iloc[i],page,cant)
					Headers = { 'api_token' : credential['ideaScale API Token'] }
					ideasText = requests.get(URL, headers=Headers)
					ideas =pd.read_json(StringIO(ideasText.text),dtype = False)

					print("Downloading Ideas... %d"%(page*cant))

		print("Cleaning Database")

		cursor.execute(f"delete from {tablename_campaigns} t1 where exists (select 1 from {tablename_campaigns}  t2 where t2.id = t1.id and t2.ctid > t1.ctid );" )
		cursor.execute(f"delete from {tablename_ideas} t1 where exists (select 1 from {tablename_ideas}  t2 where t2.id = t1.id and t2.ctid > t1.ctid );" )

		connection.commit()

		cursor.close()

		print("Download - OK")

		return {
			'statusCode': 200,
			'body': 'Download - Ok'
		}

	elif action == "download-progress":
		
		cursor = connection.cursor()

		swFaltanTablas = False
		cantidadCampaings = 0
		totalCampaings = 0
		cantidadIdeas = 0
		swMasIdeas = False

		cursor.execute("SELECT EXISTS (SELECT table_name FROM information_schema.tables WHERE table_name = '%s');"% tablename_campaigns)
		row = cursor.fetchone()
		if not row[0] :
			swFaltanTablas = True

		cursor.execute("SELECT EXISTS (SELECT table_name FROM information_schema.tables WHERE table_name = '%s');"% tablename_ideas)
		row = cursor.fetchone()
		if not row[0] :
			swFaltanTablas = True

		if not swFaltanTablas :

			query = "SELECT count(id) FROM %s;"%tablename_campaigns
			cursor.execute(query)
			results = cursor.fetchone()
			cantidadCampaings = results[0]

			URL = urlAPI + "campaigns/active"
			Headers = { 'api_token' : credential['ideaScale API Token']  }	
			campaignsText = requests.get(URL, headers=Headers)
			campaigns =pd.read_json(StringIO(campaignsText.text),dtype = False)
			totalCampaings = len(campaigns)

			query = "SELECT count(id) FROM %s;"%tablename_ideas
			cursor.execute(query)
			results = cursor.fetchone()
			cantidadIdeas = results[0]
			
			page = cantidadIdeas+1
			cant = 1
			URL = urlAPI + "ideas/%s/%s"%(page,cant)
			Headers = { 'api_token' : credential['ideaScale API Token'] }
			ideasText = requests.get(URL, headers=Headers)
			ideas =pd.read_json(StringIO(ideasText.text),dtype = False)
			swMasIdeas = (len(ideas)>0)

		swTerminado = False
		if (cantidadCampaings<totalCampaings or swMasIdeas or swFaltanTablas):

			resultado = 'Campaings: %d de %d - Ideas: %d de ... (no terminado)'%(cantidadCampaings,totalCampaings,cantidadIdeas)
		else:
			swTerminado = True
			resultado = 'Campaings: %d de %d - Ideas: %d de %d (terminado)'%(cantidadCampaings,totalCampaings,cantidadIdeas,cantidadIdeas)

			print("Cleaning Database")

			cursor.execute(f"delete from {tablename_campaigns} t1 where exists (select 1 from {tablename_campaigns}  t2 where t2.id = t1.id and t2.ctid > t1.ctid );" )
			cursor.execute(f"delete from {tablename_ideas} t1 where exists (select 1 from {tablename_ideas}  t2 where t2.id = t1.id and t2.ctid > t1.ctid );" )

			connection.commit()

		cursor.close()

		print(resultado)

		return {
			'statusCode': 200,
			'body': resultado,
			'swTerminado' : swTerminado

		}


	elif action == "translate":

		pathJsonGoogle = os.path.join(sys.path[0], "googleAPI.json")
		f = open(pathJsonGoogle)
		googleAut = json.load(f)

		for key in googleAut:
			environ[key] = googleAut[key] 
			
		environ["GOOGLE_APPLICATION_CREDENTIALS"] = pathJsonGoogle

		project_id = environ["project_id"]
		parent = "projects/%s"%project_id
		client = translate.TranslationServiceClient()

		cursor = connection.cursor()

		swFaltanTablas = False

		swExisteCampaingEsp = False
		cursor.execute("SELECT EXISTS (SELECT table_name FROM information_schema.tables WHERE table_name = '%s');"% tablename_campaigns_esp)
		row = cursor.fetchone()
		if row[0] :
			swExisteCampaingEsp = True

		cursor.execute("SELECT EXISTS (SELECT table_name FROM information_schema.tables WHERE table_name = '%s');"% tablename_campaigns)
		row = cursor.fetchone()
		if not row[0] :
			swFaltanTablas = True

		swExisteIdeasEsp = False
		cursor.execute("SELECT EXISTS (SELECT table_name FROM information_schema.tables WHERE table_name = '%s');"% tablename_ideas_esp)
		row = cursor.fetchone()
		if row[0] :
			swExisteIdeasEsp = True

		cursor.execute("SELECT EXISTS (SELECT table_name FROM information_schema.tables WHERE table_name = '%s');"% tablename_ideas)
		row = cursor.fetchone()
		if not row[0] :
			swFaltanTablas = True

		cursor.close()

		if not swFaltanTablas :
		#Si estan las tablas en ingles descargadas...
     
			if swExisteCampaingEsp:
				#si ya habia comenzado la traduccíon, cargo la lista de las campañas que faltan por traducir
				lista_campaigns = pd.read_sql_query(f"SELECT {tablename_campaigns}.id FROM   {tablename_campaigns} WHERE  NOT EXISTS ( SELECT FROM   {tablename_campaigns_esp} WHERE  {tablename_campaigns_esp}.id = {tablename_campaigns}.id);", engine)
			else:
				#si no habia comenzado la traduccíon tomo todas las campañas para traducir
				lista_campaigns = pd.read_sql_query("SELECT * FROM %s;"%tablename_campaigns , engine)

			lista_campaigns_translated = lista_campaigns.copy()

			cursor = connection.cursor()

			for i in tqdm(range(len(lista_campaigns_translated)), desc = "Traduciendo Campaings"):
				
				swExisteTraduccion = False
				if swExisteCampaingEsp :
					cursor.execute("SELECT count(id) FROM %s WHERE id='%s' "% (tablename_campaigns_esp,lista_campaigns_translated.loc[i,"id"]))
					row = cursor.fetchone()
					if row[0] > 0:
						swExisteTraduccion = True

				if not swExisteTraduccion :
					#evito traducir si ya existe la campaña... esto es una seguridad adicional producto de la concurrencia, muchas llamadas al api de traducir
               
					for colJson in columnas_traducirCampaignsJSON:
						#convierto los campos str json en estructura de datos
						campo = json.loads(json.loads(lista_campaigns_translated.loc[i,colJson]))
						lista_campaigns_translated[colJson].at[i] = campo
						
					#tradusco la campaña
					lista_campaigns_translated.loc[i,columnas_traducirCampaings] = translateColumns(lista_campaigns_translated[columnas_traducirCampaings].loc[i],columnas_traducirCampaignsJSON,client, parent)

					#clean convierte los campos tipo list, series y dict en str
					lista_campaigns_translated.loc[i,columnas_traducirCampaings]  = clean(lista_campaigns_translated.loc[i,columnas_traducirCampaings] )

					#guardo la traducción
					lista_campaigns_translated.iloc[i:i+1].to_sql (name=tablename_campaigns_esp, con=engine, if_exists='append', index = False)

			if swExisteIdeasEsp:
				#si ya habia comenzado la traduccíon, cargo la lista de las ideas que faltan por traducir
				lista_ideas = pd.read_sql_query(f"SELECT {tablename_ideas}.* FROM   {tablename_ideas} WHERE  NOT EXISTS ( SELECT FROM   {tablename_ideas_esp} WHERE  {tablename_ideas_esp}.id = {tablename_ideas}.id);", engine)
			else:
				#si no habia comenzado la traduccíon tomo todas las ideas para traducir
				lista_ideas = pd.read_sql_query("SELECT * FROM %s;"%tablename_ideas, engine)

			lista_ideas_translated = lista_ideas.copy()

			#de todas las ideas que faltan, en lugar de ir en forma ordenada, voy de forma aleatoria
         #esto evita que si hay concurrencia dos ejecuciones no trabajen con las mismas ideas
			indices_a_traducir = lista_ideas_translated.index.to_list()
			random.shuffle(indices_a_traducir)

			for i in tqdm(range(len(lista_ideas_translated)), desc = "Traduciendo Ideas"):
				
				indice_a_traducir = indices_a_traducir[i]

				swExisteTraduccion = False
				if swExisteIdeasEsp :
					cursor.execute("SELECT count(id) FROM %s WHERE id='%s' "% (tablename_ideas_esp,lista_ideas_translated.loc[indice_a_traducir,"id"]))
					row = cursor.fetchone()
					if row[0] > 0:
						swExisteTraduccion = True

				if not swExisteTraduccion :
					#evito traducir si ya existe la idea... esto es una seguridad adicional producto de la concurrencia, muchas llamadas al api de traducir
               
					for colJson in columnas_traducirIdeasJSON:
						#convierto los campos str json en estructura de datos
						campo = json.loads(json.loads(lista_ideas_translated.loc[indice_a_traducir,colJson]))
						lista_ideas_translated[colJson].at[indice_a_traducir] = campo
						
					#tradusco la idea
					lista_ideas_translated.loc[indice_a_traducir,columnas_traducirIdeas] = translateColumns(lista_ideas_translated[columnas_traducirIdeas].loc[indice_a_traducir],columnas_traducirIdeasJSON,client, parent)

					#clean convierte los campos tipo list, series y dict en str 
					lista_ideas_translated.loc[indice_a_traducir,columnas_traducirIdeas]  = clean(lista_ideas_translated.loc[indice_a_traducir,columnas_traducirIdeas] )

					#guardo la traducción
					lista_ideas_translated.iloc[indice_a_traducir:indice_a_traducir+1].to_sql (name=tablename_ideas_esp, con=engine, if_exists='append', index = False)
			
			print("Cleaning Database")

			#como seguridad adicional con esto limpio de posibles duplicados producto de la concurrencia
			cursor.execute(f"delete from {tablename_campaigns_esp} t1 where exists (select 1 from {tablename_campaigns_esp}  t2 where t2.id = t1.id and t2.ctid > t1.ctid );" )
			cursor.execute(f"delete from {tablename_ideas_esp} t1 where exists (select 1 from {tablename_ideas_esp}  t2 where t2.id = t1.id and t2.ctid > t1.ctid );" )

			connection.commit()

			cursor.close()

			print("Traduccion - OK")

			return {
				'statusCode': 200,
				'body': 'Traduccion - OK'
			}

		else:
			print("Traduccion - Error: Faltan Descargar Tablas")

			return {
				'statusCode': 200,
				'body': 'Traduccion - Error: Faltan Descargar Tablas'
			}

	elif action == "translate-progress":
		
		cursor = connection.cursor()

		swFaltanTablas = False
		cantidadCampaings = 0
		totalCampaings = 0
		cantidadIdeas = 0
		totalIdeas = 0

		cursor.execute("SELECT EXISTS (SELECT table_name FROM information_schema.tables WHERE table_name = '%s');"% tablename_campaigns_esp)
		row = cursor.fetchone()
		if not row[0] :
			swFaltanTablas = True

		cursor.execute("SELECT EXISTS (SELECT table_name FROM information_schema.tables WHERE table_name = '%s');"% tablename_campaigns)
		row = cursor.fetchone()
		if not row[0] :
			swFaltanTablas = True

		cursor.execute("SELECT EXISTS (SELECT table_name FROM information_schema.tables WHERE table_name = '%s');"% tablename_ideas_esp)
		row = cursor.fetchone()
		if not row[0] :
			swFaltanTablas = True

		cursor.execute("SELECT EXISTS (SELECT table_name FROM information_schema.tables WHERE table_name = '%s');"% tablename_ideas)
		row = cursor.fetchone()
		if not row[0] :
			swFaltanTablas = True

		if not swFaltanTablas :

			query = "SELECT count(distinct(id)) FROM %s;"%tablename_campaigns_esp
			cursor.execute(query)
			results = cursor.fetchone()
			cantidadCampaings = results[0]

			query = "SELECT count(id) FROM %s;"%tablename_campaigns
			cursor.execute(query)
			results = cursor.fetchone()
			totalCampaings = results[0]

			query = "SELECT count(distinct(id)) FROM %s;"%tablename_ideas_esp
			cursor.execute(query)
			results = cursor.fetchone()
			cantidadIdeas = results[0]

			query = "SELECT count(id) FROM %s;"%tablename_ideas
			cursor.execute(query)
			results = cursor.fetchone()
			totalIdeas= results[0]

		swTerminado = False
		porcentaje = 0

		if(totalIdeas>0):
			porcentaje = cantidadIdeas * 100 /  totalIdeas

		if (cantidadCampaings<totalCampaings or cantidadIdeas<totalIdeas or swFaltanTablas):

			resultado = 'Campaings: %d de %s - Ideas: %d de %d (no terminado)'%(cantidadCampaings,totalCampaings,cantidadIdeas,totalIdeas)

		else:
			swTerminado = True

			resultado = 'Campaings: %d de %s - Ideas: %d de %d (terminado)'%(cantidadCampaings,totalCampaings,cantidadIdeas,totalIdeas)

			print("Cleaning Database")
			#como seguridad adicional con esto limpio de posibles duplicados producto de la concurrencia
			cursor.execute(f"delete from {tablename_campaigns_esp} t1 where exists (select 1 from {tablename_campaigns_esp}  t2 where t2.id = t1.id and t2.ctid > t1.ctid );" )
			cursor.execute(f"delete from {tablename_ideas_esp} t1 where exists (select 1 from {tablename_ideas_esp}  t2 where t2.id = t1.id and t2.ctid > t1.ctid );" )

			connection.commit()

		cursor.close()

		print(resultado)

		return {
			'statusCode': 200,
			'body': resultado,
			'swTerminado': swTerminado,
			'porcentaje': porcentaje
		}


	return {
		'statusCode': 200,
		'body': 'No se ha realizado ninguna accion'
	}

#revisarCampos inicializa campos que no esten en el dafaframe en funcion del tipo
def revisarCampos(df,tipos):
	if isinstance(df , pd.DataFrame) :
		for key, value in tipos.items():
			if not key in df.columns:
				if value == int:
					df[key] = 0
				elif value == str:
					df[key] = ""
	elif isinstance(df , pd.Series) :
		auxDict= {}
		keys_index = []
		for i,column in enumerate(df.axes[0]):
			if not key in df.axes[0]:
				if value == int:
					auxDict.update({key: 0})
					keys_index += [key]

				elif value == str:
					auxDict.update({key: ""})
					keys_index += [key]

		auxSerie = pd.Series(data=auxDict, index=keys_index)
		df = df.append(auxSerie)

	return df

#applySeriesDump convierte los campos Series en str
def applySeriesDump(item):
	dictSerie = item.to_dict()
	res = json.dumps(json.dumps(dictSerie))
	return res

#clean convierte los campos tipo list, series y dict en str 
def clean(df):
	if isinstance(df , pd.DataFrame) :
		for i,column in enumerate(df.columns):
			for k in range(len(df)):
				if isinstance(df[column].iloc[ k] , list) :
					df[column] = df[column].apply(json.dumps).apply(json.dumps) 
					break
				elif isinstance(df[column].iloc[ k] , dict) :
					df[column] = df[column].apply(json.dumps).apply(json.dumps)  
					break
				elif isinstance(df[column].iloc[ k] , pd.Series) :
					df[column] = df[column].apply(applySeriesDump)  
					#df[column] = dictSerie.apply(json.dumps).apply(json.dumps)  
					break
	elif isinstance(df , pd.Series) :
		for i,column in enumerate(df.axes[0]):
			if isinstance(df[column] , list) :
				df[column]  = json.dumps(json.dumps(df[column]))
			elif isinstance(df[column] , dict) :
				df[column] = json.dumps(json.dumps(df[column]))
			elif isinstance(df[column] , pd.Series) :
				df[column] = applySeriesDump(df[column] )
	
	return df

def obtenerColumnasATraducirDeDict(dictColumna,jsonTraducir):
	colTraducir = []
	for key,c in dictColumna.items():
		if  ( key in jsonTraducir or "*" in jsonTraducir) and len(c)!=0 :
			if isinstance(c , pd.Series):
				colTraducir += obtenerColumnasATraducirDeSerie(c,jsonTraducir[key])
			elif  isinstance(c , dict)  :
				colTraducir += obtenerColumnasATraducirDeDict(c,jsonTraducir[key])
			else:
				#colTraducir += [key]
				colTraducir += [c]
	return colTraducir

def obtenerColumnasATraducirDeSerie(serie,jsonTraducir):
	colTraducir = []
	for index_c,c in enumerate(serie):
		if (  serie.axes[0][index_c] in jsonTraducir or "*" in jsonTraducir)  and len(c)!=0 :
			if isinstance(c , pd.Series) :
				colTraducir += obtenerColumnasATraducirDeSerie(c,jsonTraducir[serie.axes[0][index_c]])
			elif  isinstance(c , dict)  :
				colTraducir += obtenerColumnasATraducirDeDict(c,jsonTraducir[serie.axes[0][index_c]])
			else:
				strCol  = serie.axes[0][index_c].replace("_"," ")
				#colTraducir += [strCol]
				colTraducir += [c]
	return colTraducir


def obtenerColumnasATraducirDeList(listColumna,jsonTraducir):
	colTraducir = []

	for i,listItem in enumerate(listColumna):
		if isinstance(listItem , pd.Series) :
			colTraducir += obtenerColumnasATraducirDeSerie(listItem,jsonTraducir)
		elif  isinstance(listItem , dict)  :
			colTraducir += obtenerColumnasATraducirDeDict(listItem,jsonTraducir)
		else:
			colTraducir += [listItem]

	return colTraducir

def resultadosDeDict(dictColumna,jsonTraducir,indexTranslations,translations):
	results = {}
	for key,c in dictColumna.items():
		if  ( key in jsonTraducir or "*" in jsonTraducir) and len(c)!=0 :
			if isinstance(c , pd.Series):
				res,indexTranslations = resultadosDeSerie(c,jsonTraducir[key],indexTranslations,translations)
				results.update({key:res})
			elif isinstance(c , dict)  :
				res,indexTranslations = resultadosDeDict(c,jsonTraducir[key],indexTranslations,translations)
				results.update({key:res})
			else:
				#results.update({translations[indexTranslations]:translations[indexTranslations+1]})
				results.update({key:translations[indexTranslations]})
				indexTranslations +=1
		else:
			results.update({key:c})

	return results,indexTranslations

def resultadosDeSerie(serie,jsonTraducir,indexTranslations,translations):
	results = pd.Series()

	for index_c,c in enumerate(serie):
		if (  serie.axes[0][index_c] in jsonTraducir or "*" in jsonTraducir)  and len(c)!=0 :
			if isinstance(c , pd.Series) :
				results[serie.axes[0][index_c]],indexTranslations= resultadosDeSerie(c,jsonTraducir[serie.axes[0][index_c]],indexTranslations,translations)
			elif  isinstance(c , dict)  :
				results[serie.axes[0][index_c]],indexTranslations= resultadosDeDict(c,jsonTraducir[serie.axes[0][index_c]],indexTranslations,translations)
			else:
				#results [translations[indexTranslations]] = translations[indexTranslations+1]
				results [serie.axes[0][index_c]] = translations[indexTranslations]
				indexTranslations += 1
		else:
			results[serie.axes[0][index_c]] = c

	return results,indexTranslations


def resultadosDeList(listColumna,jsonTraducir,indexTranslations,translations):
	results = []

	for listItem in listColumna:
		if isinstance(listItem , pd.Series) :
			res,indexTranslations = resultadosDeSerie(listItem,jsonTraducir,indexTranslations,translations)
			results += [res]
		elif  isinstance(listItem , dict)  :
			res,indexTranslations = resultadosDeDict(listItem,jsonTraducir,indexTranslations,translations)
			results += [res]
		else:
			results += [translations[indexTranslations]]
			indexTranslations += 1
	return results,indexTranslations


#traduce las columnas
def translateColumns(columns,columnas_traducirJSON,client, parent)	:

	#crea una lista flat con todos los campos y subcampos a traducir
	colTraducir = []
	for index_c,c in enumerate(columns):
		if len(c)!=0 :
			if isinstance(c , pd.Series) and columns.axes[0][index_c] in columnas_traducirJSON :
				colTraducir += obtenerColumnasATraducirDeSerie(c,columnas_traducirJSON[columns.axes[0][index_c]])
			elif  isinstance(c , dict)  :
				colTraducir += obtenerColumnasATraducirDeDict(c,columnas_traducirJSON[columns.axes[0][index_c]])
			elif isinstance(c , list) and columns.axes[0][index_c] in columnas_traducirJSON :
				colTraducir += obtenerColumnasATraducirDeList(c,columnas_traducirJSON[columns.axes[0][index_c]])
			else:
				colTraducir += [c]

	totalChars = len("".join(colTraducir))

	response_translations = []

	
	if(totalChars<maxChars):
		#chekea si puede hacer la traduccion completa de todos los elementos en una sola llamada
		response = client.translate_text(
			contents=colTraducir,
			mime_type="text/html",
			source_language_code="en-US",
			target_language_code="es",
			parent=parent
		)

		#guarda los resultados en una lista
		for res in response.translations:
			response_translations += [res.translated_text]

	else:
		#hace la traduccion de elemento en elemento
      
		for text in colTraducir:

			totalCharsText = len(text)

			if(totalCharsText == 0):
				#no traduce si el elemento es vacio
				response_translations += [""]

			else:


				if(totalCharsText<maxChars):
					#si el elemento puede traducirse en una sola llamanda
               
					response = client.translate_text(
						contents=[text],
						mime_type="text/html",
						source_language_code="en-US",
						target_language_code="es",
						parent=parent
					)

					#guardo los resultados
					response_translations += [response.translations[0].translated_text]

				else:

					#si el elemento tiene que traducirse en varias llamandas lo divido en lineas
               
					lines = textwrap.wrap(text, maxChars-1, break_long_words=False)
					results = []
					for line in lines:
						response = client.translate_text(
							contents=[line],
							mime_type="text/html",
							source_language_code="en-US",
							target_language_code="es",
							parent=parent
						)

						#guardo los resultados de esta linea
						results += [response.translations[0].translated_text]

					#guardo los resultados de todas las lineas juntas
					results_str= ' '.join(results)
					response_translations += [results_str]


	#recupero los campos y subcampos de la lista de resultados
   
	results = columns
	indexTranslations = 0
	for index_c,c in enumerate(columns):
		if len(c)!=0 :
			if isinstance(c , pd.Series) and columns.axes[0][index_c] in columnas_traducirJSON :
				results[columns.axes[0][index_c]],indexTranslations= resultadosDeSerie(c,columnas_traducirJSON[columns.axes[0][index_c]],indexTranslations,response_translations)
			elif  isinstance(c , dict)  :
				results[columns.axes[0][index_c]],indexTranslations= resultadosDeDict(c,columnas_traducirJSON[columns.axes[0][index_c]],indexTranslations,response_translations)
			elif isinstance(c , list) and columns.axes[0][index_c] in columnas_traducirJSON :
				results[columns.axes[0][index_c]],indexTranslations= resultadosDeList(c,columnas_traducirJSON[columns.axes[0][index_c]],indexTranslations,response_translations)
			else:
				results[columns.axes[0][index_c]] = response_translations[indexTranslations]
				indexTranslations += 1
		else:
			results[columns.axes[0][index_c]] = ""


	return results
	

	
	