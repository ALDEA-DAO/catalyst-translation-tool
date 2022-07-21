

from lambda_function import lambda_handler

from os import environ

environ["LOCAL RUN"] = "True"


print("INIT")

lambda_handler({'action':"download",'dbname':"manuel_3"}, None)
#lambda_handler({'action':"download-progress",'dbname':"new"}, None)
#lambda_handler({'action':"translate",'dbname':"manuel_2"}, None)
#lambda_handler({'action':"translate-progress",'dbname':"manuel_1"}, None)
#lambda_handler({'action':"setMostrarTabla",'dbname':"manuel_1","nombreProyecto":"FUND 8"}, None)
