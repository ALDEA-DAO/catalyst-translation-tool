

import sys
from os import environ

#la url de la REST API de idea scale
urlAPI = "https://cardano.ideascale.com/a/rest/v1/"


if "LOCAL RUN" in environ and environ["LOCAL RUN"] or "C:\\Users" in sys.path[0]:

	#Si se quiere se puede definir datos para sesion de uso local, para testing

	environ["LOCAL RUN"] = "True"

	credential = {

		#Datos de conexión PostgreSQL

		'username':'COMPLETAR CON DATOS DE CONEXIÓN DE POSTGRESQL',
		'password':'COMPLETAR CON DATOS DE CONEXIÓN DE POSTGRESQL',
		'host':'COMPLETAR CON DATOS DE CONEXIÓN DE POSTGRESQL',
		'db':'COMPLETAR CON DATOS DE CONEXIÓN DE POSTGRESQL',

		#Datos de conexión REST API de idea scale

		'ideaScale API Token': 'COMPLETAR CON TOKEN DE IDEASCALE' 
	}

else:

	#Aquí se detallan los datos de conexión en producción.

	environ["LOCAL RUN"] = "False"

	credential = {
		
		#Datos de conexión PostgreSQL

		'username':'COMPLETAR CON DATOS DE CONEXIÓN DE POSTGRESQL',
		'password':'COMPLETAR CON DATOS DE CONEXIÓN DE POSTGRESQL',
		'host':'COMPLETAR CON DATOS DE CONEXIÓN DE POSTGRESQL',
		'db':'COMPLETAR CON DATOS DE CONEXIÓN DE POSTGRESQL',

		#ADatos de conexión REST API de idea scale

		'ideaScale API Token': 'COMPLETAR CON TOKEN DE IDEASCALE'
		  
	}


#id bigint,
#name text COLLATE pg_catalog."default",
#tagline text COLLATE pg_catalog."default",
#description text COLLATE pg_catalog."default",
#"summaryEnabled" boolean,
#summary text COLLATE pg_catalog."default",
#"templateId" bigint,
#template text COLLATE pg_catalog."default",
#"privateCampaign" boolean,
#"votingAllowed" boolean,
#"groupId" bigint,
#"funnelId" bigint,
#"groupName" text COLLATE pg_catalog."default",
#"archivedCampaign" boolean,
#"startDate" text COLLATE pg_catalog."default",
#"hideIdeaAuthor" boolean,
#"hideCommentAuthor" boolean,
#"bannerImage" text COLLATE pg_catalog."default",
#"logoImage" text COLLATE pg_catalog."default",
#"ideaCount" bigint,
#"voteCount" bigint,
#"commentCount" bigint,
#"authorizedGroupIds" text COLLATE pg_catalog."default",
#"ideaFromUnauthorizedMemberAllowed" boolean,
#"ideaSubmitFormInstruction" text COLLATE pg_catalog."default",
#"memberIdeaSubmissionAllowed" boolean,
#"memberIdeaAttachmentAllowed" boolean,
#"memberIdeaAttachmentMandatory" boolean,
#"authorEdit" boolean,
#"userSubscriptionAllowed" boolean,
#"moderatorAdminOnlyIdeasEnabled" boolean,
#"forceAuthorizedMemberOnlyEnabled" boolean,
#"moderatorAdminOnlyIdeasNotificationEnabled" boolean,
#"campaignStatusName" text COLLATE pg_catalog."default",
#"showTagline" boolean,
#"publicOwnerName" text COLLATE pg_catalog."default",
#"tagsRequired" boolean,
#"stageStatistics" text COLLATE pg_catalog."default",
#"campaignUrl" text COLLATE pg_catalog."default",
#"newCampaign" boolean
#"featureImage" text

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

campaignsColumnsSQL = []
for i in range(len(campaignsColumns)):
	campaignsColumnsSQL += ["\""+campaignsColumns[i]+"\""]

columnasCampaignsConHTML = ['description','summary']
columnasCampaignsConLists = []

columnasCampaignsConJSON= {"stageStatistics" : {"label"}}


columnas_traducirCampaings = ["name","tagline","description","summary","ideaSubmitFormInstruction","campaignStatusName","stageStatistics"]

columnas_traducirCampaignsJSON= {"stageStatistics" : {"label"}}


#id bigint,
#"creationDateTime" text COLLATE pg_catalog."default",
#"editedAt" text COLLATE pg_catalog."default",
#"statusChangeDate" text COLLATE pg_catalog."default",
#title text COLLATE pg_catalog."default",
#text text COLLATE pg_catalog."default",
#"campaignId" bigint,
#"campaignName" text COLLATE pg_catalog."default",
#"authorId" bigint,
#"authorInfo" text COLLATE pg_catalog."default",
#"voteCount" bigint,
#"upVoteCount" bigint,
#"downVoteCount" bigint,
#"myVote" bigint,
#"commentCount" bigint,
#url text COLLATE pg_catalog."default",
#tags text COLLATE pg_catalog."default",
#"funnelId" bigint,
#"funnelName" text COLLATE pg_catalog."default",
#"statusId" bigint,
#status text COLLATE pg_catalog."default",
#"stageId" bigint,
#"stageName" text COLLATE pg_catalog."default",
#"stageLabel" text COLLATE pg_catalog."default",
#flag text COLLATE pg_catalog."default",
#"customFieldsByKey" text COLLATE pg_catalog."default",
#"campaignCustomFields" text COLLATE pg_catalog."default",
#"ideaNumber" bigint,
#labels text COLLATE pg_catalog."default",
#contributors text COLLATE pg_catalog."default",
#attachments text COLLATE pg_catalog."default",
#"attachmentDetails" text COLLATE pg_catalog."default"


##customFieldsByKey:
#problem_solution
#what_does_success_for_this_project_look_like_ 
#please_describe_your_proposed_solution
#please_provide_a_detailed_budget_breakdown
#media
#what_main_challenges_or_risks_do_you_foresee_to_deliver_this_project_successfully_
#relevant_experience
#please_provide_details_of_your_team_members_required_to_complete_the_project
#please_describe_how_your_proposed_solution_will_address_the_challenge_
#requested_funds
#sdg_rating
#please_describe_how_you_will_measure_the_progress_and_the_development_of_the_project_
#please_provide_a_detailed_plan_and_timeline_for_delivering_the_solution
#website_github_repository__not_required_

##campaignCustomFields:
#Please provide details of your team members required to complete the project.
#Please describe your proposed solution.
#Please provide a detailed plan and timeline for delivering the solution.
#SDG rating
#What does success for this project look like?
#Website/GitHub repository (if relevant)
#Media (YouTube link)
#What main challenges or risks do you foresee to deliver this project successfully?
#Please describe how you will measure the progress and the development of the project?
#Summarize your solution to the problem
#Please describe how your proposed solution will address the challenge?
#Please provide information on whether this proposal is a continuation of a previously funded project in Catalyst or an entirely new one.
#Requested funds in USD
#Please provide a detailed budget breakdown.
#Summarize your relevant experience

#OTRA VERSION

##customFieldsByKey:
#can_you_articulate_the_gap_between_the_current_state_and_the_expected_or_envisioned_state_
#how_might_the_value_of_solving_this_problem_be_quantified_and_or_measured___optional_

##campaignCustomFields:
#Can you articulate the gap between the current state and the expected or envisioned state? 
#How might the value of solving this problem be quantified and/or measured? (optional)



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

ideasColumnsSQL = []
for i in range(len(ideasColumns)):
	ideasColumnsSQL += ["\""+ideasColumns[i]+"\""]


columnasIdeasConHTML = ['text','customFieldsByKey','campaignCustomFields']
columnasIdeasConLists = ['tags']

columnasIdeasConJSON = {"authorInfo" : {"profileQuestions": {"*"}},'customFieldsByKey':{'*'},'campaignCustomFields':{'*'},'contributors':{"profileQuestions": {"*"}},"attachmentDetails": {"*"}}



columnas_traducirIdeas = ["title","text","campaignName","authorInfo","tags","funnelName","stageLabel","flag","customFieldsByKey","campaignCustomFields","contributors"]

columnas_traducirIdeasJSON = {"authorInfo" : {"profileQuestions": {"*"}},'tags':{'*'},'customFieldsByKey':{'*'},'campaignCustomFields':{'*'},'contributors':{"profileQuestions": {"*"}}}

