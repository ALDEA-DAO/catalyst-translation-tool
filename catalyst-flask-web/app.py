# app.py
from sqlalchemy import create_engine
from flask import Flask, render_template
from werkzeug.exceptions import abort
from flask import Markup, url_for, request
import json
from os import environ

app = Flask(__name__)

from settings import credential,campaignsColumns,campaignsColumnsSQL,columnasCampaignsConHTML,columnasCampaignsConLists,columnasCampaignsConJSON , ideasColumns,ideasColumnsSQL,columnasIdeasConHTML,columnasIdeasConLists,columnasIdeasConJSON



def get_db_connection():

	engine = create_engine('postgresql://'+credential['username']+':'+credential['password']+'@'+credential['host']+':5432/' + credential['db'])

	connection = engine.raw_connection()

	return engine,connection

def cleanHTMLAndMarkupCampoDict(campoDict):
	results = {}
	for key,campo in campoDict.items():

		#if isinstance(campo , pd.Series):
		#	res = resultadosDeSerie(campo)
		#	results.update({key:res})
		#el
		if isinstance(campo , dict)  :
			res = resultadosDeDict(campo)
			results.update({key:res})
		else:
			campo  = cleanHTMLCampo (campo)
			campo = Markup(campo)

			results.update({key:campo})

	return results

def cleanHTMLAndMarkupCampoSeries(serie):
	results = pd.Series()

	for index_c,campo in enumerate(serie):
		#if isinstance(campo , pd.Series) :
		#	results[serie.axes[0][index_c]]= cleanHTMLAndMarkupCampoSeries(campo)
		#el
		if  isinstance(campo , dict)  :
			results[serie.axes[0][index_c]]= cleanHTMLAndMarkupCampoDict(campo)
		else:
			campo  = cleanHTMLCampo (campo)
			campo = Markup(campo)

			results[serie.axes[0][index_c]] = campo
		
	return results


def cleanHTMLAndMarkupCampoList(campoList):
	results = []

	for campo in campoList:
		#if isinstance(campo , pd.Series) :
		#	res = cleanHTMLAndMarkupCampoSeries(campo)
		#	results += [res]
		#el
		if  isinstance(campo , dict)  :
			res = cleanHTMLAndMarkupCampoDict(campo)
			results += [res]
		else:

			campo  = cleanHTMLCampo (campo)
			campo = Markup(campo)

			results += [campo]

	return results

def cleanHTMLCampo(strText):

	res = strText
	#res = res.replace('\\ "','\\"')

	#listTags = ["p","li","ul","br","b","i","strong","span","div","hr","a","u"]

	#for tag in listTags:
	#	res = res.replace('< %s>'%tag,'<%s>'%tag).replace('< /%s>'%tag,'</%s>'%tag).replace('</ %s>'%tag,'</%s>'%tag).replace('<%s >'%tag,'<%s>'%tag).replace('</%s >'%tag,'</%s>'%tag)

	return res			



@app.route('/',methods = ['GET','POST'])

#@app.route('/page/<pagination>/')
#@app.route('/page/<pagination>/order/<orderby>')
#@app.route('/page/<pagination>/order/<orderby>/<orderdir>/')

#@app.route('/tag/<tag>/')
#@app.route('/tag/<tag>/page/<pagination>/')
#@app.route('/tag/<tag>/page/<pagination>/order/<orderby>')
#@app.route('/tag/<tag>/page/<pagination>/order/<orderby>/<orderdir>/')

#@app.route('/tag/<tag>/search//')
#@app.route('/tag/<tag>/search//page/<pagination>/')
#@app.route('/tag/<tag>/search//page/<pagination>/order/<orderby>')
#@app.route('/tag/<tag>/search//page/<pagination>/order/<orderby>/<orderdir>/')

#@app.route('/search/<search>/')
#@app.route('/search/<search>/page/<pagination>/')
#@app.route('/search/<search>/page/<pagination>/order/<orderby>')
#@app.route('/search/<search>/page/<pagination>/order/<orderby>/<orderdir>/')

#@app.route('/tag//search/<search>/')
#@app.route('/tag//search/<search>/page/<pagination>/')
#@app.route('/tag//search/<search>/page/<pagination>/order/<orderby>')
#@app.route('/tag//search/<search>/page/<pagination>/order/<orderby>/<orderdir>/')


#@app.route('/tag//search//',methods = ['POST'])
#@app.route('/tag//search//page/<pagination>/')
#@app.route('/tag//search//page/<pagination>/order/<orderby>')
#@app.route('/tag//search//page/<pagination>/order/<orderby>/<orderdir>/')


def index( pagination="1", orderby= "voteCount",orderdir="desc",tag="",search=""):

	swLocalRun = environ["LOCAL RUN"] == "True"

	engine,connection = get_db_connection()
	cur = connection.cursor()

	cur.execute('SELECT nombre,"nombreSQL" FROM "mostrarTabla" WHERE id = 1')
	proyecto = cur.fetchone()
	nombreProyecto = proyecto[0]
	nombreTablas = proyecto[1]

	cur.execute('SELECT * FROM campaigns_esp_%s;'%(nombreTablas))
	campaigns = cur.fetchall()

	campaigns_dict = []
	for campaign in campaigns:
		campaign_dict = {}
		for i in range(len(campaignsColumns)):
			campo = campaign[i]
			if not campo is None and len(str(campo))>0 :
				if campaignsColumns[i] in columnasCampaignsConJSON or campaignsColumns[i] in columnasCampaignsConLists:
					try:
						campo =  json.loads(json.loads(campo))
					except:
						#strCampo = campo.replace('\\ "','\\"')
						#campo =  json.loads(json.loads(strCampo))
						pass
					if campaignsColumns[i] in columnasCampaignsConHTML:
						if  isinstance(campo , dict)  :
							campo = cleanHTMLAndMarkupCampoDict(campo)
						elif isinstance(campo , list) :
							campo = cleanHTMLAndMarkupCampoList(campo)
						else:
							campo  = cleanHTMLCampo (campo)
							campo = Markup(campo)
				else:
					if campaignsColumns[i] in columnasCampaignsConHTML:
						campo  = cleanHTMLCampo (campo)
						campo = Markup(campo)
			campaign_dict.update({campaignsColumns[i]:campo})

		campaigns_dict += [campaign_dict]
		

	if request.method == 'POST':
		search = request.form['search']
	else:
		pagination = request.args.get('pagination') if "pagination" in request.args else pagination
		orderby= request.args.get('orderby') if "orderby" in request.args else orderby
		orderdir= request.args.get('orderdir') if "orderdir" in request.args else orderdir
		tag= request.args.get('tag') if "tag" in request.args else tag
		search= request.args.get('search') if "search" in request.args else search

	pagination = int(pagination)

	print("pagination ")
	print (pagination)
	print("orderby ")
	print (orderby)
	print("orderdir ")
	print (orderdir)
    #campaign_dict.update({campaignsColumns[i]:html.unescape(campaign[i])})
	
	print("swLocalRun")
	print (swLocalRun)

	print("TAG")
	print (tag)

	print("SEARCH")

	if request.method == 'POST':
		print("POST")
		search = request.form['search']

	print (search)

	

	if tag != "":

		tagJson = json.dumps(tag)
		tagJson = tagJson.replace("\"","")
		tagJson = json.dumps(tagJson)
		tagJson = tagJson.replace("\"","")
		tagJson = tagJson.replace("\\","\\\\")

		busqueda = ' \'%\\\\"' + tagJson + '\\\\"%\''

		cur.execute(f'SELECT count(id) FROM ideas_esp_{nombreTablas} where tags LIKE {busqueda}')

	
	else:
		if search != "":
			busqueda = '%' + search + '%'
			cur.execute(f'SELECT count(id) FROM ideas_esp_{nombreTablas} where title LIKE \'{busqueda}\' or text LIKE \'{busqueda}\' or \"campaignCustomFields\" LIKE \'{busqueda}\' or \"customFieldsByKey\" LIKE \'{busqueda}\' ')


		else:
			cur.execute('SELECT count(id) FROM ideas_esp_%s'%(nombreTablas))


	cantIdeas = cur.fetchone()[0]

	limit = 15

	if cantIdeas > 0:
			cantMaxPages = (cantIdeas // limit)+1
	else: 
		cantMaxPages = 1

	if pagination<1:
		pagination = 1

	if pagination>cantMaxPages:
		pagination = cantMaxPages
	
	if pagination>1 :
		pageAnt = pagination -1
	else:
		pageAnt = 0

	if pagination<cantMaxPages :
		pageNext = pagination +1
	else:
		pageNext = 0

	

	offset = (int(pagination)-1 )*limit

	if tag != "":

		tagJson = json.dumps(tag)
		tagJson = tagJson.replace("\"","")
		tagJson = json.dumps(tagJson)
		tagJson = tagJson.replace("\"","")
		tagJson = tagJson.replace("\\","\\\\")

		busqueda = ' \'%\\\\"' + tagJson + '\\\\"%\''

		#print (busqueda)

		cur.execute(f'SELECT * FROM ideas_esp_{nombreTablas} where tags LIKE {busqueda} order by "{orderby}" {orderdir} limit {limit} OFFSET {offset};')

		
	else:
		if search != "":
			busqueda = '%' + search + '%'
			cur.execute(f'SELECT * FROM ideas_esp_{nombreTablas} where title LIKE \'{busqueda}\' or text LIKE \'{busqueda}\' or \"campaignCustomFields\" LIKE \'{busqueda}\' or \"customFieldsByKey\" LIKE \'{busqueda}\'  order by "{orderby}" {orderdir} limit {limit} OFFSET {offset};')
		else:

			cur.execute('SELECT * FROM ideas_esp_%s order by "%s" %s limit %d OFFSET %d;'%(nombreTablas,orderby,orderdir,limit,offset))


	ideas = cur.fetchall()



	ideas_dict = []
	for idea in ideas:
		idea_dict = {}
		for i in range(len(ideasColumns)):
			campo = idea[i]
			if not campo is None and len(str(campo))>0 :
				if ideasColumns[i] in columnasIdeasConJSON or ideasColumns[i] in columnasIdeasConLists:
					try:
						campo =  json.loads(json.loads(campo))
					except:
						#strCampo = campo.replace('\\ "','\\"')
						#campo =  json.loads(json.loads(strCampo))
						pass
					if ideasColumns[i] in columnasIdeasConHTML:
						if  isinstance(campo , dict)  :
							campo = cleanHTMLAndMarkupCampoDict(campo)
						elif isinstance(campo , list) :
							campo = cleanHTMLAndMarkupCampoList(campo)
						else:
							campo  = cleanHTMLCampo (campo)
							campo = Markup(campo)
				else:
					if ideasColumns[i] in columnasIdeasConHTML:
						campo  = cleanHTMLCampo (campo)
						campo = Markup(campo)
			idea_dict.update({ideasColumns[i]:campo})

		ideas_dict += [idea_dict]


	cur.close()
	connection.close()

	

	return render_template('index.html',nombreProyecto=nombreProyecto, campaigns=campaigns_dict,ideas=ideas_dict,orderby=orderby,orderdir=orderdir,cantIdeas=cantIdeas,cantPaginas=cantMaxPages,cantPorPag=limit,pagination= pagination,pageAnt=pageAnt,pageNext=pageNext,swLocalRun=swLocalRun,tag=tag,search=search)




@app.route('/campaign/<int:campaign_id>')
@app.route('/campaign/<int:campaign_id>/page/<pagination>/')
@app.route('/campaign/<int:campaign_id>/page/<pagination>/order/<orderby>')
@app.route('/campaign/<int:campaign_id>/page/<pagination>/order/<orderby>/<orderdir>/')
def campaign(campaign_id,pagination="1",orderby= "voteCount",orderdir="desc"):

	print ("campaign: %s " %campaign_id)
	engine,connection = get_db_connection()
	cur = connection.cursor()

	cur.execute('SELECT nombre,"nombreSQL" FROM "mostrarTabla" WHERE id = 1')
	proyecto = cur.fetchone()
	nombreProyecto = proyecto[0]
	nombreTablas = proyecto[1]

	cur.execute('SELECT * FROM campaigns_esp_%s;'%(nombreTablas))
	campaigns = cur.fetchall()

	campaigns_dict = []
	for campaign in campaigns:
		campaign_dict = {}
		for i in range(len(campaignsColumns)):
			campo = campaign[i]
			if not campo is None and len(str(campo))>0 :
				if campaignsColumns[i] in columnasCampaignsConJSON or campaignsColumns[i] in columnasCampaignsConLists:
					try:
						campo =  json.loads(json.loads(campo))
					except:
						#strCampo = campo.replace('\\ "','\\"')
						#campo =  json.loads(json.loads(strCampo))
						pass
					if campaignsColumns[i] in columnasCampaignsConHTML:
						if  isinstance(campo , dict)  :
							campo = cleanHTMLAndMarkupCampoDict(campo)
						elif isinstance(campo , list) :
							campo = cleanHTMLAndMarkupCampoList(campo)
						else:
							campo  = cleanHTMLCampo (campo)
							campo = Markup(campo)
				else:
					if campaignsColumns[i] in columnasCampaignsConHTML:
						campo  = cleanHTMLCampo (campo)
						campo = Markup(campo)
			campaign_dict.update({campaignsColumns[i]:campo})

		campaigns_dict += [campaign_dict]


	cur.execute('SELECT %s FROM campaigns_esp_%s WHERE id = %s' %(','.join(campaignsColumnsSQL),nombreTablas,campaign_id))

	campaign = cur.fetchone()

	if campaign is None :
		abort(404)
		print ("no existe")
	else:
		#print (campaign)

		campaign_dict = {}
		for i in range(len(campaignsColumns)):
			campo = campaign[i]
			if not campo is None and len(str(campo))>0 :
				if campaignsColumns[i] in columnasCampaignsConJSON or campaignsColumns[i] in columnasCampaignsConLists:
					try:
						campo =  json.loads(json.loads(campo))
					except:
						#strCampo = campo.replace('\\ "','\\"')
						#campo =  json.loads(json.loads(strCampo))
						pass
					if campaignsColumns[i] in columnasCampaignsConHTML:
						if  isinstance(campo , dict)  :
							campo = cleanHTMLAndMarkupCampoDict(campo)
						elif isinstance(campo , list) :
							campo = cleanHTMLAndMarkupCampoList(campo)
						else:
							campo  = cleanHTMLCampo (campo)
							campo = Markup(campo)
				else:
					if campaignsColumns[i] in columnasCampaignsConHTML:
						campo  = cleanHTMLCampo (campo)
						campo = Markup(campo)
			campaign_dict.update({campaignsColumns[i]:campo})

		#print ("NAME: %s"%campaign_dict['name'])

	
		pagination = int(pagination)

		print("pagination ")
		print (pagination)
		print("orderby ")
		print (orderby)
		print("orderdir ")
		print (orderdir)
		 #campaign_dict.update({campaignsColumns[i]:html.unescape(campaign[i])})
	

		cur.execute('SELECT count(id) FROM ideas_esp_%s where "campaignId" = %s'%(nombreTablas,campaign_dict['id']))

		cantIdeas = cur.fetchone()[0]


		limit = 15

		if cantIdeas > 0:
			cantMaxPages = (cantIdeas // limit) + 1
		else: 
			cantMaxPages = 1

		if pagination<1:
			pagination = 1

		if pagination>cantMaxPages:
			pagination = cantMaxPages
	
		if pagination>1 :
			pageAnt = pagination -1
		else:
			pageAnt = 0

		if pagination<cantMaxPages :
			pageNext = pagination +1
		else:
			pageNext = 0


		offset = (int(pagination)-1 )*limit



		cur.execute('SELECT * FROM ideas_esp_%s where "campaignId" = %s order by "%s" %s limit %d OFFSET %d;'%(nombreTablas,campaign_dict['id'],orderby,orderdir,limit,offset))

		ideas = cur.fetchall()

		ideas_dict = []
		for idea in ideas:
			idea_dict = {}
			for i in range(len(ideasColumns)):
				campo = idea[i]
				if not campo is None and len(str(campo))>0 :
					if ideasColumns[i] in columnasIdeasConJSON or ideasColumns[i] in columnasIdeasConLists:
						try:
							campo =  json.loads(json.loads(campo))
						except:
							#strCampo = campo.replace('\\ "','\\"')
							#campo =  json.loads(json.loads(strCampo))
							pass
						if ideasColumns[i] in columnasIdeasConHTML:
							if  isinstance(campo , dict)  :
								campo = cleanHTMLAndMarkupCampoDict(campo)
							elif isinstance(campo , list) :
								campo = cleanHTMLAndMarkupCampoList(campo)
							else:
								campo  = cleanHTMLCampo (campo)
								campo = Markup(campo)
					else:
						if ideasColumns[i] in columnasIdeasConHTML:
							campo  = cleanHTMLCampo (campo)
							campo = Markup(campo)
				idea_dict.update({ideasColumns[i]:campo})

			ideas_dict += [idea_dict]

	cur.close()
	connection.close()


	
	return render_template('campaign.html',nombreProyecto=nombreProyecto, campaigns = campaigns_dict, campaign=campaign_dict, ideas=ideas_dict,orderby=orderby,orderdir=orderdir,cantIdeas=cantIdeas,cantPaginas=cantMaxPages,cantPorPag=limit,pagination= pagination,pageAnt=pageAnt,pageNext=pageNext,tag="",search="")


@app.route('/campaign/<int:campaign_id>/acerca')
def campaign_acerca(campaign_id):

	print ("campaign: %s " %campaign_id)
	engine,connection = get_db_connection()
	cur = connection.cursor()

	cur.execute('SELECT nombre,"nombreSQL" FROM "mostrarTabla" WHERE id = 1')
	proyecto = cur.fetchone()
	nombreProyecto = proyecto[0]
	nombreTablas = proyecto[1]

	cur.execute('SELECT * FROM campaigns_esp_%s;'%(nombreTablas))
	campaigns = cur.fetchall()

	campaigns_dict = []
	for campaign in campaigns:
		campaign_dict = {}
		for i in range(len(campaignsColumns)):
			campo = campaign[i]
			if not campo is None and len(str(campo))>0 :
				if campaignsColumns[i] in columnasCampaignsConJSON or campaignsColumns[i] in columnasCampaignsConLists:
					try:
						campo =  json.loads(json.loads(campo))
					except:
						#strCampo = campo.replace('\\ "','\\"')
						#campo =  json.loads(json.loads(strCampo))
						pass
					if campaignsColumns[i] in columnasCampaignsConHTML:
						if  isinstance(campo , dict)  :
							campo = cleanHTMLAndMarkupCampoDict(campo)
						elif isinstance(campo , list) :
							campo = cleanHTMLAndMarkupCampoList(campo)
						else:
							campo  = cleanHTMLCampo (campo)
							campo = Markup(campo)
				else:
					if campaignsColumns[i] in columnasCampaignsConHTML:
						campo  = cleanHTMLCampo (campo)
						campo = Markup(campo)
			campaign_dict.update({campaignsColumns[i]:campo})

		campaigns_dict += [campaign_dict]


	cur.execute('SELECT %s FROM campaigns_esp_%s WHERE id = %s' %(','.join(campaignsColumnsSQL),nombreTablas,campaign_id))

	campaign = cur.fetchone()

	if campaign is None :
		abort(404)
		print ("no existe")
	else:
		#print (campaign)

		campaign_dict = {}
		for i in range(len(campaignsColumns)):
			campo = campaign[i]
			if not campo is None and len(str(campo))>0 :
				if campaignsColumns[i] in columnasCampaignsConJSON or campaignsColumns[i] in columnasCampaignsConLists:
					try:
						campo =  json.loads(json.loads(campo))
					except:
						#strCampo = campo.replace('\\ "','\\"')
						#campo =  json.loads(json.loads(strCampo))
						pass
					if campaignsColumns[i] in columnasCampaignsConHTML:
						if  isinstance(campo , dict)  :
							campo = cleanHTMLAndMarkupCampoDict(campo)
						elif isinstance(campo , list) :
							campo = cleanHTMLAndMarkupCampoList(campo)
						else:
							campo  = cleanHTMLCampo (campo)
							campo = Markup(campo)
				else:
					if campaignsColumns[i] in columnasCampaignsConHTML:
						campo  = cleanHTMLCampo (campo)
						campo = Markup(campo)
			campaign_dict.update({campaignsColumns[i]:campo})

		#print ("NAME: %s"%campaign_dict['name'])


	cur.close()
	connection.close()


	
	return render_template('campaign-acerca.html',nombreProyecto=nombreProyecto, campaigns = campaigns_dict, campaign=campaign_dict)


@app.route('/idea/<int:idea_id>')
def idea(idea_id):

	print ("idea: %s " %idea_id)
	engine,connection = get_db_connection()
	cur = connection.cursor()

	cur.execute('SELECT nombre,"nombreSQL" FROM "mostrarTabla" WHERE id = 1')
	proyecto = cur.fetchone()
	nombreProyecto = proyecto[0]
	nombreTablas = proyecto[1]

	cur.execute('SELECT %s FROM ideas_esp_%s WHERE id = %s' %(','.join(ideasColumnsSQL),nombreTablas,idea_id))

	idea = cur.fetchone()

	

	if idea is None :
		abort(404)
		print ("no existe")
	else:

		idea_dict = {}
		for i in range(len(ideasColumns)):
			campo = idea[i]
			if not campo is None and len(str(campo))>0 :
				if ideasColumns[i] in columnasIdeasConJSON or ideasColumns[i] in columnasIdeasConLists:
					try:
						campo =  json.loads(json.loads(campo))
					except:
						#strCampo = campo.replace('\\ "','\\"')
						#campo =  json.loads(json.loads(strCampo))
						pass
					if ideasColumns[i] in columnasIdeasConHTML:
						if  isinstance(campo , dict)  :
							campo = cleanHTMLAndMarkupCampoDict(campo)
						elif isinstance(campo , list) :
							campo = cleanHTMLAndMarkupCampoList(campo)
						else:
							campo  = cleanHTMLCampo (campo)
							campo = Markup(campo)
				else:
					if ideasColumns[i] in columnasIdeasConHTML:
						campo  = cleanHTMLCampo (campo)
						campo = Markup(campo)
			idea_dict.update({ideasColumns[i]:campo})

		swImagenIdea =  isinstance(  idea_dict['attachmentDetails'],list) and  len(idea_dict['attachmentDetails'])>0

		cur.execute('SELECT * FROM campaigns_esp_%s;'%(nombreTablas))
		campaigns = cur.fetchall()

		campaigns_dict = []
		for campaign in campaigns:

			campaign_dict = {}
			for i in range(len(campaignsColumns)):
				campo = campaign[i]
				if not campo is None and len(str(campo))>0 :
					if campaignsColumns[i] in columnasCampaignsConJSON or campaignsColumns[i] in columnasCampaignsConLists:
						try:
							campo =  json.loads(json.loads(campo))
						except:
							#strCampo = campo.replace('\\ "','\\"')
							#campo =  json.loads(json.loads(strCampo))
							pass
						if campaignsColumns[i] in columnasCampaignsConHTML:
							if  isinstance(campo , dict)  :
								campo = cleanHTMLAndMarkupCampoDict(campo)
							elif isinstance(campo , list) :
								campo = cleanHTMLAndMarkupCampoList(campo)
							else:
								campo  = cleanHTMLCampo (campo)
								campo = Markup(campo)
					else:
						if campaignsColumns[i] in columnasCampaignsConHTML:
							campo  = cleanHTMLCampo (campo)
							campo = Markup(campo)
				campaign_dict.update({campaignsColumns[i]:campo})
			campaigns_dict += [campaign_dict]


		cur.execute('SELECT %s FROM campaigns_esp_%s WHERE id = %s' %(','.join(campaignsColumnsSQL),nombreTablas,idea_dict['campaignId']))

		campaign = cur.fetchone()

		if campaign is None :
			abort(404)
			print ("no existe")
		else:
			#print (campaign)

			campaign_dict = {}
			for i in range(len(campaignsColumns)):
				campo = campaign[i]
				if not campo is None and len(str(campo))>0 :
					if campaignsColumns[i] in columnasCampaignsConJSON or campaignsColumns[i] in columnasCampaignsConLists:
						try:
							campo =  json.loads(json.loads(campo))
						except:
							#strCampo = campo.replace('\\ "','\\"')
							#campo =  json.loads(json.loads(strCampo))
							pass
						if campaignsColumns[i] in columnasCampaignsConHTML:
							if  isinstance(campo , dict)  :
								campo = cleanHTMLAndMarkupCampoDict(campo)
							elif isinstance(campo , list) :
								campo = cleanHTMLAndMarkupCampoList(campo)
							else:
								campo  = cleanHTMLCampo (campo)
								campo = Markup(campo)
					else:
						if campaignsColumns[i] in columnasCampaignsConHTML:
							campo  = cleanHTMLCampo (campo)
							campo = Markup(campo)
				campaign_dict.update({campaignsColumns[i]:campo})

		cur.execute('SELECT count(id) FROM ideas_esp_%s where "campaignId" = %s;'%(nombreTablas,campaign_dict['id']))
		totalIdeas = cur.fetchone()[0]




	cur.close()
	connection.close()
	

	return render_template('idea.html', nombreProyecto=nombreProyecto, campaigns = campaigns_dict, campaign = campaign_dict, idea=idea_dict,totalIdeas = totalIdeas)


