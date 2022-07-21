#!/bin/bash
set -e

publish_function_code(){
	echo "Deploying the code itself..."
	cd ${INPUT_LAMBDA_PYTHON_FOLDER}
	zip -r code.zip  * -x \*.git\* \*__pycache__\* \*venv\* \*.no_upload\*
	local result2=$(aws lambda update-function-code --function-name "${INPUT_LAMBDA_FUNCTION_NAME}" --zip-file fileb://code.zip)
	rm code.zip
	cd ..
	
}


install_zip_dependencies(){
	echo "Installing and zipping dependencies..."

	mkdir python
	pip install --target=python -r "${INPUT_LAMBDA_PYTHON_FOLDER}/${INPUT_REQUIREMENTS_TXT}"
	zip -r dependencies.zip ./python


}

publish_dependencies_as_layer(){
	
	echo "Publishing dependencies as a layer..."
	
	echo "Using the INPUT_LAMBDA_LAYER_ARN:"
	echo "${INPUT_LAMBDA_LAYER_ARN}"	
	echo "Using the INPUT_LAMBDA_LAYER_NAME:"
	echo "${INPUT_LAMBDA_LAYER_NAME}"	
	
	local result=$(aws lambda publish-layer-version --layer-name "${INPUT_LAMBDA_LAYER_ARN}" --zip-file fileb://dependencies.zip)
	
	LAYER_VERSION=$(jq '.Version' <<< "$result")
	echo "LAYER VERSION:"
	echo ${LAYER_VERSION}

	rm -rf python
	rm dependencies.zip
}


update_function_layers(){
		
	echo "LAYER LISTA ANTES DE SUBIR EL NUEVO:"
	aws lambda get-function-configuration --function-name "${INPUT_LAMBDA_FUNCTION_NAME}" --query "{Layers: Layers}"

	local result=$(aws lambda get-function-configuration --function-name "${INPUT_LAMBDA_FUNCTION_NAME}" )
	
	echo "LAYER LISTA sin LAYER QUE VOYA REEMPLAZAR:"
	LAYER_LISTA2=$(jq -r ".Layers | .[] | .Arn | select(test( \"${INPUT_LAMBDA_LAYER_NAME}\" ; \"gipx\")==false)" <<< "$result") || echo "error 2"
	echo ${LAYER_LISTA2}

	echo "Using the layer in the function..."
	echo "${INPUT_LAMBDA_LAYER_ARN}:${LAYER_VERSION}"
	echo "LAYER LISTA completa:"
	echo "${INPUT_LAMBDA_LAYER_ARN}:${LAYER_VERSION} ${LAYER_LISTA2}"
	
	aws lambda update-function-configuration --function-name "${INPUT_LAMBDA_FUNCTION_NAME}" --layers ${INPUT_LAMBDA_LAYER_ARN}:${LAYER_VERSION} ${LAYER_LISTA2}
}

deploy_lambda_function(){
	
	
	if [ "${INPUT_LAMBDA_UPDATE_FUNCTION_CODE}" == 'true' ]; then
		echo "UPDATE FUNCTION CODE:"
		publish_function_code
	fi
	
	if [ "${INPUT_LAMBDA_CREATE_LAYERS}" == 'true' ]; then
		echo "UPDATE LAYERS:"

		local chars=$(wc --chars < "${INPUT_LAMBDA_PYTHON_FOLDER}/${INPUT_REQUIREMENTS_TXT}")
		echo "len requirements: "$chars

		

		if [ $chars == 0 ]; then
			echo "requirements file is empty"
		else
			install_zip_dependencies

			mfs=$(du -s --apparent-size --block-size=1  ./python | awk '{ print $1}')
			echo "folder size = ${mfs}"
			
			if [ $mfs == 4096 ]; then
				echo "requirements file is empty"

				rm -rf python
				rm dependencies.zip

			else
				publish_dependencies_as_layer
				update_function_layers
			fi
		fi
	fi
	
}

deploy_lambda_function
echo "Done."
