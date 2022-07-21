﻿

*******************************************  

## **Aldea Devs**  
### **Traductor de Project Catalyst**  

*******************************************  

**Source Code:**   
https://github.com/manupadillaph/Catalyst  

*******************************************  

El desarrollo esta compuesto de cuatro partes: 
1. **Catalyst-backend-web:** web de administración que interactua con la API de descarga y traducción (Catalyst-download-translate-api) y setea la traducción a mostrar en la web en español.  
2. **Catalyst-download-translate-api:** servicios API generados a partir de la función de AWS Lambda Catalyst-download-translate. 
3. **Catalyst-download-translate:** función de AWS Lambda que realiza la descarga desde la Api de IdeaScale y hace las traducciones con la Api de Google Translate.  
4. **Catalyst-flask-web:** es la web en español.  


*******************************************  

### **Catalyst-backend-web**

*******************************************  

**Source Code:** `catalyst-backend-web/`  

Es una página HTML con un formulario que realiza peticiones usando Javascript al API `catalyst-download-translate-api`  

Hay cinco botones y sus funciones estan detalladas en la función lambda: `Catalyst-download-translate` 

**IMPLEMENTACION:**  

La página fué implementada en AWS Amplify.  
  
La aplicación de AWS Amplify se actualiza automáticamente al subir a github cualquier cambio en esta carpeta: `catalyst-backend-web/`  

Eso es gracias al workflow definido en: `.github/workflows/deploy-catalyst-backend-web.yml` 
  
Allí se deben setear:
```
with:
	web_folder: 'catalyst-backend-web'
	amplify_app_name: 'catalyst-backend-web'
	s3_bucket: 'catalyst.translation'
env:
	AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
	AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
	AWS_DEFAULT_REGION: ${{ secrets.AWS_REGION }}
```

Donde `amplify_app_name` es el nombre de la aplicación de AWS Amplify y `s3_bucket` es el AWS S3 Bucket donde se sube un zip que luego se usa para actualizar la página en AWS Amplify.    
 
Los secrets de github se configuran en:  
https://github.com/<USUARIO\>/<REPOSITORIO\>/settings/secrets/actions  

Tal y como se explica aquí:  
https://docs.github.com/en/actions/security-guides/encrypted-secrets

Los valores utilizados se toman desde AWS IAM:   
https://us-east-1.console.aws.amazon.com/iam/home#/security_credentials  

La URL del servicio de API debe ser configura en el archivo: `catalyst-backend-web/settings.js`  

```
////Completar con la URL del servicio creado de API de download y traducción a partir del código en 'catalyst-download-translate'  
catalyst_api_url = "Completar con la URL del servicio de API";

```

*******************************************  

### **Catalyst-download-translate-api**

*******************************************  

**IMPLEMENTACION:**    
  
Es un servicio que fué creado en AWS para exponer en forma de API una función Labmda.  
  
Este API Gateway conecta las peticiones con la función Lambda `catalyst-download-translate` donde se realizan las acciones solicitadas.  

Para crear un API Gateway a partir de una funcion Lambda seguir estos pasos una vez este creada la función Lambda:  
https://docs.aws.amazon.com/es_es/lambda/latest/dg/services-apigateway.html  
https://docs.aws.amazon.com/es_es/apigateway/latest/developerguide/api-gateway-create-api-as-simple-proxy-for-lambda.html  


*******************************************  

### **Catalyst-download-translate**  

*******************************************   

**Source Code:** `catalyst-download-translate/`  
  
Es un código Python que corre en una función Lambda AWS y se ejecuta a partir de una llamada API.  
Cada vez que se recibe una llamada se ejecuta en un segundo plano la solicitud.  
La forma de ver el progreso de una petición (descarga o traducción) es mediante otra llamada que solicita el progreso.  

La función se conecta con una base de datos PostgreSQL y guarda en ella las campañas y ideas descargadas y traducidas desde ideaScale Catalyst.
  
Para descargar las campañas e ideas se conecta con el `API de Ideascale`  

Documentación de la API IdeaScale:  
https://support.ideascale.com/en/articles/682876-ideascale-rest-api#get-started-  
https://a.ideascale.com/api-docs/index.html  

Se necesita un api token de Ideascale, que se puede crear en: https://app.ideascale.com/a/person/communities/api-tokens  
 
Para traducir utiliza el `API de Google Translate`.  
Se necesita el archivo `googleAPI.json` para utilizar el servicio.  
Seguir los pasos aquí para obtener el archivo: https://cloud.google.com/translate/docs/setup  

La función recibe por POST las acciones requeridas desde la web de `catalyst-backend-web` mediante el Api `Catalyst-download-translate-api`.   
  
Las acciones posibles son: 
  
- **Download:** Con el sufijo de nombre de tabla especificado crea las tablas respectivas de campañas e ideas para hacer la descarga desde el API de Ideascale.   
  Por ejemplo si ingresamos el sufijo 'test' creará las tablas: 'capaigns_test' y 'ideas_test'.  
  Si el sufijo de nombre de tabla existe se eliminarán las tablas anteriores y se realizará una nueva descarga.  
  Una vez finalizada la descarga devuelve un JSON:
```
	{
		'statusCode': 200,
		'body': 'Download - Ok'
	}
```

- **Download-Progress:** Revisa el progreso de la descarga en las tablas con el sufijo de nombre de tabla especificado.  
  Devuelve un JSON si no esta terminada aún la descarga:
  ```
	{
		'statusCode': 200,
		'body': 'Campaings: %d de %d - Ideas: %d de ... (no terminado)',
		'swTerminado' : False
	}
  ```
  O si ya está terminada:  
  ```
	{
		'statusCode': 200,
		'body': 'Campaings: %d de %d - Ideas: %d de %d (terminado),
		'swTerminado' : True
	}
  ```
- **Translate:** Crea dos nuevas tablas con el sufijo correspondiente para almacenar la traducción en español y comienza la traducción utilizando el API de Google Translate.  
  Por ejemplo si ingresamos el sufijo 'test' creará las tablas: 'capaigns_esp_test' y 'ideas_esp_test'.  
  Una vez finalizada la descarga devuelve un JSON:  
  ```
    {
		'statusCode': 200,
		'body': 'Traduccion - OK'
	}
  ```
  Si se intenta traducir con un sufijo de tabla que no se encuentra creada aún por el proceso de descarga devolverá:
  ```
    {
		'statusCode': 200,
		'body': 'Traduccion - Error: Faltan Descargar Tablas'
	}
  ```
- **Translate-Progress:** 
  Revisa el progreso de la traducción en las tablas en las tablas con el sufijo de nombre de tabla especificado.  
  Devuelve un JSON si no esta terminada aún la traducción:
  ```
	{
		'statusCode': 200,
		'body': 'Campaings: %d de %d - Ideas: %d de %d (no terminado)',
		'swTerminado' : False,
		'porcentaje': porcentaje
	}
  ```
  O si ya está terminada:  
  ```
	{
		'statusCode': 200,
		'body': 'Campaings: %d de %d - Ideas: %d de %d (terminado),
		'swTerminado' : True
		'porcentaje': porcentaje
	}
  ```
  
- **Setear Tabla a mostrar y nombre del Proyecto:** Setea las tablas traducidas en español y el nombre del proyecto que se van a mostrar en la página en español.  
	Por ejemplo si ingresamos el sufijo 'test' y el nombre del proyecto 'Fund 8', la web en español usará las tablas 'capaigns_esp_test' y 'ideas_esp_test' y organizará las camapañas bajo el nombre 'Fund 8'.  
    Devuelve un JSON:
  ```
	{
		'statusCode': 200,
		'swSetMostrarTabla': True
	}
  ```

La API de ideascale actuamente trae los siguientes campos de cada campaña:

```
id, name, tagline, description,  
summaryEnabled, summary, templateId, template,  
privateCampaign, votingAllowed, groupId, funnelId,  
groupName, archivedCampaign, startDate, hideIdeaAuthor,  
hideCommentAuthor, bannerImage, logoImage, ideaCount,  
voteCount, commentCount, authorizedGroupIds, ideaFromUnauthorizedMemberAllowed,  
ideaSubmitFormInstruction, memberIdeaSubmissionAllowed, 
memberIdeaAttachmentAllowed, memberIdeaAttachmentMandatory,  
authorEdit, userSubscriptionAllowed, 
moderatorAdminOnlyIdeasEnabled, forceAuthorizedMemberOnlyEnabled,  
moderatorAdminOnlyIdeasNotificationEnabled, 
campaignStatusName, showTagline, publicOwnerName,  
tagsRequired, stageStatistics, campaignUrl, newCampaign 
```

Y de cada idea:  
```
id, creationDateTime, editedAt, statusChangeDate,  
title, text, campaignId, campaignName,  
authorId, authorInfo, voteCount, upVoteCount,  
downVoteCount, myVote, commentCount, url,  
tags, funnelId, funnelName, statusId,  
status, stageId, stageName, stageLabel,  
flag, customFieldsByKey, campaignCustomFields, ideaNumber,  
labels, contributors, attachments, attachmentDetails  
```
  
Algunos de estos campos son del tipo JSON conteniendo otros campos adentro.  
   
Idea.customFieldsByKey:

```
problem_solution,   
what_does_success_for_this_project_look_like_,  
please_describe_your_proposed_solution,   
please_provide_a_detailed_budget_breakdown,    
media,   
what_main_challenges_or_risks_do_you_foresee_to_deliver_this_project_successfully_,   
relevant_experience,   
please_provide_details_of_your_team_members_required_to_complete_the_project,   
please_describe_how_your_proposed_solution_will_address_the_challenge_,   
requested_funds,   
sdg_rating,   
please_describe_how_you_will_measure_the_progress_and_the_development_of_the_project_,   
please_provide_a_detailed_plan_and_timeline_for_delivering_the_solution,   
website_github_repository__not_required_ 
```

Idea.campaignCustomFields:  

``` 
Please provide details of your team members required to complete the project.,   
Please describe your proposed solution.,   
Please provide a detailed plan and timeline for delivering the solution.,   
SDG rating,   
What does success for this project look like?,   
Website/GitHub repository (if relevant),   
Media (YouTube link),   
What main challenges or risks do you foresee to deliver this project successfully?,   
Please describe how you will measure the progress and the development of the project?,   
Summarize your solution to the problem,   
Please describe how your proposed solution will address the challenge?,   
Please provide information on whether this proposal is a continuation of a previously funded project in Catalyst or an entirely new one.,   
Requested funds in USD,   
Please provide a detailed budget breakdown.,   
Summarize your relevant experience   
```

Algunas ideas tienen una versión de subcampos diferentes en lugar de los arriba mencionados: 

Idea.customFieldsByKey:  
```
can_you_articulate_the_gap_between_the_current_state_and_the_expected_or_envisioned_state_,   
how_might_the_value_of_solving_this_problem_be_quantified_and_or_measured___optional_
```

Idea.campaignCustomFields: 

```
Can you articulate the gap between the current state and the expected or envisioned state?,    
How might the value of solving this problem be quantified and/or measured? (optional)
```  

**IMPLEMENTACION:**   

Se creó una función Lambda con el código Python.  
  
La función de AWS se actualiza automáticamente al subir a github cualquier cambio en la carpeta: `catalyst-download-translate/`, gracias a los siguientes workflows: `.github/workflows/deploy-catalyst-down-trans-no-req.yml` y `.github/workflows/deploy-catalyst-down-trans-only-reqs.yml`
  
Los workflows necesitan los siguientes datos a especificar:

```
with:
	lambda_python_folder: 'catalyst-download-translate'
	lambda_function_name: 'catalyst-download-translate'
	lambda_update_function_code: 'true' | 'false'
	lambda_create_layers: 'true' | 'false'
	lambda_layer_arn: 'arn:aws:lambda:COMPLETAR'
	lambda_layer_name: 'catalyst-dependences'
env:
	AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
	AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
	AWS_DEFAULT_REGION: ${{ secrets.AWS_REGION }}

```

Donde `lambda_function_name` es el nombre de la función Lambda AWS a actualizar, `lambda_update_function_code` y `lambda_create_layers` determinan que cosas se han de actualizar, `lambda_layer_arn` y `lambda_layer_name` son el arn y el nombre del layer que se actualizará con las dependencias de requrements.txt.

Si se modifica el archivo `requirements.txt` con módulos de python nuevos, estos se implementan en el layer `catalyst-dependences` que se le asigna a la función.  
    
**Layers que utiliza:**  
- Catalyst-dependences: Es dinámico. Se actualiza automáticamente al cambiar el archivo `requirements.txt`.  
- SQLAlchemy   
- Pandas 
- Aws-psycopg2   

Estos layers fueron descargados desde aquí:  
https://github.com/keithrozario/Klayers  
https://api.klayers.cloud//api/v2/p3.8/layers/latest/ap-southeast-2/html  

Y cargados como layers manualmente en la función.  
 
La base de datos PostgreSQL fué creada en **AWS RDS**

Los datos para realizar la conexión con la misma se especifican en el archivo: `catalyst-download-translate/settings.py`

```
username: 'xxxxxxx',  
password: 'xxxxxxx',  
host:  'xxxxxxx',  
db: 'xxxxxxx'  
```

El Api token para conectarse con la API de Ideascale se setea también en el archivo: `catalyst-download-translate/settings.py`  
```
'ideaScale API Token': 'xxxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx'  
```

Para obtener el token:   
Crear un usuario y loguearse en https://app.ideascale.com/a/person/profile/  
Solicitar token en: https://app.ideascale.com/a/person/communities/api-tokens  
Documentación de la API: 
https://support.ideascale.com/en/articles/682876-ideascale-rest-api#authentication  

Los campos que se obtienen de Ideascale deben estar detallados en el archivo de settings: `catalyst-download-translate/settings.py`  
Alli hay que especificar todos los campos que se van a leer y guardar en la base de datos y el tipo de datos que tiene cada uno.  

```

campaignsColumns = ['id', 'name', 'tagline', 'description', "summaryEnabled", 'summary', "templateId", 'template', "privateCampaign", "votingAllowed", "groupId", "funnelId", "groupName", "archivedCampaign", "startDate", "hideIdeaAuthor", "hideCommentAuthor", "bannerImage", "logoImage", "ideaCount", "voteCount", "commentCount", "authorizedGroupIds", "ideaFromUnauthorizedMemberAllowed", "ideaSubmitFormInstruction", "memberIdeaSubmissionAllowed", "memberIdeaAttachmentAllowed", "memberIdeaAttachmentMandatory", "authorEdit", "userSubscriptionAllowed", "moderatorAdminOnlyIdeasEnabled", "forceAuthorizedMemberOnlyEnabled", "moderatorAdminOnlyIdeasNotificationEnabled", "campaignStatusName", "showTagline", "publicOwnerName", "tagsRequired", "stageStatistics", "campaignUrl", "newCampaign","featureImage"]
	
campaignsColumnsTipos  = {
	"id" : int,
	"name" : str,
	"tagline" : str,
	"description" : str,
	"summaryEnabled" : bool,
	"summary" : str,
	"templateId" : int,
	"template" : str,
	"privateCampaign" : bool,
	"votingAllowed" : bool,
	"groupId" : int,
	"funnelId" : int,
	"groupName" : str,
	"archivedCampaign" : bool,
	"startDate" : str,
	"hideIdeaAuthor" : bool,
	"hideCommentAuthor" : bool,
	"bannerImage" : str,
	"logoImage" : str,
	"ideaCount" : int,
	"voteCount" : int,
	"commentCount" : int,
	"authorizedGroupIds" : str,
	"ideaFromUnauthorizedMemberAllowed" : bool,
	"ideaSubmitFormInstruction" : str,
	"memberIdeaSubmissionAllowed" : bool,
	"memberIdeaAttachmentAllowed" : bool,
	"memberIdeaAttachmentMandatory" : bool,
	"authorEdit" : bool,
	"userSubscriptionAllowed" : bool,
	"moderatorAdminOnlyIdeasEnabled" : bool,
	"forceAuthorizedMemberOnlyEnabled" : bool,
	"moderatorAdminOnlyIdeasNotificationEnabled" : bool,
	"campaignStatusName" : str,
	"showTagline" : bool,
	"publicOwnerName" : str,
	"tagsRequired" : bool,
	"stageStatistics" : str,
	"campaignUrl" : str,
	"newCampaign" : bool,
	"featureImage" : str
}


ideasColumns = ['id', "creationDateTime", "editedAt", "statusChangeDate", 'title', 'text', "campaignId", "campaignName", "authorId", "authorInfo", "voteCount", "upVoteCount", "downVoteCount", "myVote", "commentCount", 'url', 'tags', "funnelId", "funnelName", "statusId", 'status', "stageId", "stageName", "stageLabel", 'flag', "customFieldsByKey", "campaignCustomFields", "ideaNumber", 'labels', 'contributors', 'attachments', "attachmentDetails"]

ideasColumnsTipos  = {
	"id": int,
	"creationDateTime" : str,
	"editedAt" : str,
	"statusChangeDate" : str,
	"title" : "text",
	"text" : str,
	"campaignId": int,
	"campaignName" : str,
	"authorId": int,
	"authorInfo" : str,
	"voteCount": int,
	"upVoteCount": int,
	"downVoteCount": int,
	"myVote": int,
	"commentCount": int,
	"url" : str,
	"tags" : str,
	"funnelId": int,
	"funnelName" : str,
	"statusId": int,
	"status" : str,
	"stageId": int,
	"stageName" : str,
	"stageLabel" : str,
	"flag" : str,
	"customFieldsByKey" : str,
	"campaignCustomFields" : str,
	"ideaNumber": int,
	"labels" : str,
	"contributors" : str,
	"attachments" :  str,
	"attachmentDetails" :  str
}

```

Ademas hay que especificar el tipo de contenido que traen los campos desde la API de Ideascale para saber como tratar con ellos.  

- Los campos con HTML son aquellos que al traducir deberán ser tratados como HTML, que llevan etiquetas y que solo se traducirá el contenido fuera de las etiquetas.  
- Los campos con Lists son aquellos que traen una lista como contenido, que debe ser traducido elemento por elemento.  
- Los campos con JSON son aquellos que vienen con una estructura JSON y que sólo se traduce parte de esa estructura: se traduce el contenido, no las llaves.

```

columnasCampaignsConHTML = ['description','summary']
columnasCampaignsConLists = []
columnasCampaignsConJSON= {"stageStatistics" : {"label"}}

columnasIdeasConHTML = ['text','customFieldsByKey','campaignCustomFields']
columnasIdeasConLists = ['tags']
columnasIdeasConJSON = {"authorInfo" : {"profileQuestions": {"*"}},'customFieldsByKey':{'*'},'campaignCustomFields':{'*'},'contributors':{"profileQuestions": {"*"}},"attachmentDetails": {"*"}}

```

Por ejemplo, el campo `authorInfo` que viene de Ideascale es del tipo JSON.  
Dentro de él esta el subcampo: `profileQuestions`.  
El * se usa para seleccionar a todos los subcampos adentro también.  

Las credenciales para usar el servicio de Google Translate están en el archivo `googleAPI.json` que debe estar presente junto al código en: 
`catalyst-download-translate/googleAPI.json`
  
Para conseguir el archivo `googleAPI.json` ir a: https://cloud.google.com/translate/docs/setup  

  
Para la traducción hay que elegir que columnas serán traducidas y de los campos JSON, que subcampos serán traducidos (especificar {'*'} para todos los sub campos):  

```

columnas_traducirCampaings = ["name","tagline","description","summary","ideaSubmitFormInstruction","campaignStatusName","stageStatistics"]

columnas_traducirCampaignsJSON= {"stageStatistics" : {"label"}}

columnas_traducirIdeas = ["title","text","campaignName","authorInfo","tags","funnelName","stageLabel","flag","customFieldsByKey","campaignCustomFields","contributors"]

columnas_traducirIdeasJSON = {"authorInfo" : {"profileQuestions": {"*"}},'tags':{'*'},'customFieldsByKey':{'*'},'campaignCustomFields':{'*'},'contributors':{"profileQuestions": {"*"}}}


```

Las funciones Lambda tienen por máximo de tiempo de ejecución unos 15 minutos.  
  
Esto tiene algunas consecuencias a tener en cuenta:  

-  En cuanto a la descarga no hay problema, suele poder hacerse por completo en una sola ejecución.
Por eso no se desarrolló un sistema de continuación y es por eso también que se sobre escriben las tablas si se inicia de nuevo con el mismo sufijo de nombre de tabla.

-  En cambio, la traducción va a verse interrumpida varias veces. Requiere mucho más de quince minutos para terminarase. Es por eso que deberemos ejecutar varias veces esta tarea.  
El proceso en total puede tomar de 1 a 2 horas. 
Cada vez que iniciemos la traducción el código va a revisar que traducciones faltan y retomará desde allí.  
También es posible abrir varios exploradores y ejecutar en paralelo varias llamadas a la API de traducciones. 
Con ello el tiempo de espera total se verá reducido por que se estarán ejecutando en paralelo varios procesos de 15 minutos cada uno.  
  
- Una vez iniciada una llamada de descarga o traducción no hay desarrollado un sistema de stop. 
  Se ejecutará hasta terminar la tarea o hasta alcanzar los 15 minutos de ejecución.  Esto ha sido parte de un problema serio que se detallará a continuación.  


*******************************************  

### **Factura excesiva por los usos de Google Translate**  

*******************************************   

Este ha sido el gran inconveniente con el que nos hemos encontrado y que ha frenado el progreso y la correcta finalización de este proyecto.  

Lamentablemente ninguno de los que formabamos parte del equipo había tenido experiencia usando el servicio pago de Google Translate. 

En la primera parte del desarrollo se uso el servicio gratuito pero en vistas de sus limitaciones se decidió pasar al servicio pago.  

El servicio gratuito no permite hacer traducciones muy extensas y algunos campos que llegaban desde Ideascale eran más extensos de lo que permitía el servicio por solicitud.

Además estaba limitada la cantidad de solicitudes por mes a 300.  

El proceso de desarrollo implico descargar varias veces todo el contenido desde Ideascale y guardarlo en diferentes versiones de tablas.

Al principio se uso sqlite3 como motor de base de datos para luego pasar a postgreSQL.   

Además, al comienzo todos los campos que venían desde Ideascale fueron tratados por igual. Luego nos dimos cuenta que algunos tenían HTML, otros una lista de otros campos y otros un JSON con muchos subcampos dentro.   
  
Comprender como tratar a cada campo y traducir correctamente todo el campo o parte de él implico hacer la traducción completa de todas las ideas varias vecces.  

Lamentablemente no especificamos límites diarios al contratar el servicio y al paso de un mes, cuando llego la factura no lo podíamos creer: nos estaban cargando con más de 9000 USD por el servicio brindado.  
  
Aquí estan detalladas las quotas del servicio pago:  
https://cloud.google.com/translate/quotas

Esto ha sido un error nuestro, claramente, pero que nos ha dejado sin la posibilidad de dejar este servicio corriendo y actualizado con las últimas campañas e ideas.  

La última version descargada y traducida por completa es la del `Fund 8`.  

Esperamos ahora que alguien pueda brindar una ayuda para restablecer el servicio y traducir las campañas e ideas del `Fund 10`.
  
Para ello se necesita:  

- Más presupuesto para ejectuar el servicio pago de Google Translate, esta vez estableciendo límites de uso diario y sabiendo que se hará una sola traducción completa en un determinado momento. El sistema esta probado y no tendría que haber necesidad de hacer más pruebas o cambios. 
- Modificar el código para utilizar otro servicio de traducción.

*******************************************  

### **Catalyst-flask-web**  

*******************************************   

**Source Code:** `catalyst-flask-web/`
  
Es una web basada en Python, Flask y Zappa que utliza templates para renderizar páginas que estan basadas en la web actual de Proyect Catalyst en Ideascale y que se conecta a una base de datos postgreSQL para obtener la información de las campañas e ideas.   

Imita a la página oficial actual de Proyect Catalyst en Ideascale: https://cardano.ideascale.com/ pero con el contenido en español y muchas funcionalidades reducidas.  

**IMPLEMENTACION:**   

Fué implementada mediante una función Lambda y un API Gateway de AWS.   
  
**URL Acceso:**  
  https://ghfhpuj6x5.execute-api.ap-southeast-2.amazonaws.com/dev  
  
La función Lambda se actualiza automáticamente al subir a github cambios en la carpeta `catalyst-flask-web/` gracias a los workflows: `.github/workflows/deploy-catalyst-flask-web-no-reqs` y `.github/workflows/deploy-catalyst-flask-web-only-reqs.yml`
  
Los workflows necesitan los siguientes datos a especificar:

```
with:
	lambda_python_folder: 'catalyst-flask-web'
	lambda_function_name: 'catalyst-flask-web'
	lambda_update_function_code: 'true' | 'false'
	lambda_create_layers: 'true' | 'false'
	lambda_layer_arn: 'arn:aws:lambda:COMPLETAR'
	lambda_layer_name: 'catalyst-dependences-zappa-flask'
env:
	AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
	AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
	AWS_DEFAULT_REGION: ${{ secrets.AWS_REGION }}
```

Donde `lambda_function_name` es el nombre de la función Lambda AWS a actualizar, `lambda_update_function_code` y `lambda_create_layers` determinan que cosas se han de actualizar, `lambda_layer_arn` y `lambda_layer_name` son el arn y el nombre del layer que se actualizará con las dependencias de requrements.txt.
  
Si se actualiza el archivo `requirements.txt` con módulos de python que se necesiten, estos se cargan en el layer `catalyst-dependences-zappa-flask` que se le asigna a la función.  
  
**Layers** que utiliza:  
- catalyst-dependences-zappa-flask: DINÁMICO, Se actualiza automáticamente al cambiar el archivo `requirements.txt` en github 
- Flask  
- Zappa  
- SQLAlchemy  
- Aws-psycopg2  
   
Estos layers fueron descargados desde aquí:  
  https://github.com/keithrozario/Klayers  
  https://api.klayers.cloud//api/v2/p3.8/layers/latest/ap-southeast-2/html  

Y cargados de forma manual en la función Lambda.  

Los datos para realizar la conexión con la base de datos se especifican en el archivo: `catalyst-flask-web/settings.py`

```
username: 'xxxxxxx',  
password: 'xxxxxxx',  
host:  'xxxxxxx',  
db: 'xxxxxxx'  
```

También es necesario especificar en el archivo de `settings.py` las columnas de las campañas e ideas y su contenido al igual que en `catalyst-download-translate`  


*******************************************   

Esta función de AWS fue creada automáticamente utilizando ZAPPA:
https://github.com/zappa/Zappa  

Zappa ayuda a crear aplicaciones de flask y subirla a AWS. 
Crea roles de ejecución, la función de Lambda, un API Gateway y un bucket donde almacena la web (catalyst-zappa)  

La configuración para usar Zappa esta en: `zappa_settings.json` 

``` 
"s3_bucket": "catalyst-zappa",
"aws_region": "ap-southeast-2"
``` 

Donde `s3_bucket` es el S3 Bucket de AWS que se usará para subir un zip que luego se usará para actualizar la función Lambda.  
  
Tutorial Zappa:  
https://pythonforundergradengineers.com/deploy-serverless-web-app-aws-lambda-zappa.html  

Tutorial Flask:  
https://www.digitalocean.com/community/tutorials/how-to-make-a-web-application-using-flask-in-python-3#step-6-displaying-a-single-post  

No es necesario usar Zappa para actualizar la función o implementar nuevos cambios.   

La acción de Github creada hace todo lo necesario.   

*******************************************  

### **Acciones automáticas de GitHub**

*******************************************  
    
Hay **acciones y workflows de github** creados para actualizar automáticamente las aplicaciones y funciones de AWS. Estas acciones se activan al modificar código o archivos dentro de las diferentes carpetas. Las carpetas que dicen `.no_upload` se usan para evitar que lo que este allí sea enviado a la función de AWS correspondiente.   
  
Cada workflow se activa al modificar el contenido de determinada carpeta o archivo y actualiza determinada función, layer o aplicación de AWS.  
  
Los workflow usan acciones definidas en `.github\actions`  
  
La acción python-to-lambda fue tomada de: `mariamrf/py-lambda-action@v1.0.0`  
  
Cada workflow esta detallado en los archivos dentro de `.github/workflows/`  
  
Se puede ver el progreso de cada workflow en:  
  https://github.com/<USUARIO\>/<REPOSITORIO\>/actions  
  
*******************************************  
    
**Comandos para instalar y usar Zappa:**  
  
Ir a la carpeta donde esta el código.   

Ejemplo:   
```
cd C:\Users\<USUARIO\>\source\repos\<REPOSITORIO\>\catalyst-flask-web  
```

Crear entorno virtual:   
```
python -m venv venv   
```
Activar entorno virtual:   
```
venv\Scripts\activate   
```
Instalar dependencias:  
```
pip install zappa  
pip install flask  
```
Usar Zappa:  
```
zappa init  
export FLASK_APP=app   
```
Crear archivo de dependencias:  
```
pip freeze > requirements.txt  
```
Exportar y subir a AWS:  
```
zappa deploy dev  
```
Actualizar AWS:  
```
zappa update dev  
```
Exportar ZIP para subir manualmente a AWS:  
```
zappa package dev  
```  
*******************************************  

**Comandos para exportar dependencias de Python y subirlas manualmente a un layer de AWS:**


1. Instalar docker y ubuntu  
2. Abrir consolar y ejecutar:  
```
docker run -it ubuntu   
```
3. En ubuntu escribir y ejecutar:  
```
apt update  
apt install software-properties-common  
add-apt-repository ppa:deadsnakes/ppa  
apt install python3.8  
apt install python3-pip  
apt install zip  
apt install python3.8-distutils  
apt install python3.8-dev  
apt install vim  
```
4. Crear carpeta python para instalar los módulos  
```
mkdir -p ./python  
cd python  
mkdir -p ./python  
```
5. Instalar los módulos en esa carpeta  
```
  pip install requests -t ./python  
  pip install pandas -t ./python  
  pip install numpy -t ./python  
```
6. Remove whl files, *.dist-info, and __pycache__. Prepare new zip.zip archive:  
```
  cd python  
  rm -r *.whl *.dist-info __pycache__  
  find ${python} -type d -name 'tests' -exec rm -rfv {} +  
  find ${python} -type d -name '__pycache__' -exec rm -rfv {} +  
  cd ..  
```
6. Hacer ZIP de esa carpeta  
```
  zip -r mypackage.zip *  
```
7. Para poder copiar ese zip del docker a windows abro otra consola y escribo:  
```
container id  
docker ps -a
```

8. Copiar el archivo a nuestro sistema de archivos de windows:  
```
docker cp <Container-ID:path_of_zip_file>  <path_where_you_want_to_copy>
```
Por ej.:  
```
docker cp 92c807c23709:python/mypackage.zip .  
```
9. Subirlo como ZIP a un layer de AWS  
