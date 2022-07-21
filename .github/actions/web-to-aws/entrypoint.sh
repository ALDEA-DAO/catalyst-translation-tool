#!/bin/bash
set -e

createl_zip(){
	echo "Creating Zip from Web folder..."
	zip -r web.zip ${INPUT_WEB_FOLDER} -j
}

publish_zip(){
	
	echo "Publishing zip in amplify..."
	
	echo "Using the INPUT_AMPLIFY_APP_NAME:"
	echo "${INPUT_AMPLIFY_APP_NAME}"	
	
	
	local result=$(aws amplify list-apps)


	APP_ID=$(jq -r ".apps[] | select(.name == \"${INPUT_AMPLIFY_APP_NAME}\" ) | .appId" <<< "$result")

	echo "Using the APP_ID:"
	echo "${APP_ID}"	

	BRANCH_NAME=$(jq -r ".apps[] | select(.name == \"${INPUT_AMPLIFY_APP_NAME}\" ) | .productionBranch | .branchName" <<< "$result")

	echo "Using the BRANCH_NAME:"
	echo "${BRANCH_NAME}"	


	archive="web.zip"
	s3_bucket="${S3_BUCKET}"
	amplify_id="${APP_ID}"
	git_branch="${BRANCH_NAME}"

	# Save the archive to S3 with the MD5 checksum in metadata to simplify 
	# checks in the next deployment
	aws s3 cp $archive s3://$s3_bucket/
	rm web.zip

	# Start the deployment
	printf "Start Amplify deployment\n"
	aws amplify start-deployment \
		--app-id $amplify_id \
		--branch-name $git_branch \
		--source-url s3://$s3_bucket/$archive > amplify-deploy-job.json

	AMPLIFY_JOB_ID=$(cat amplify-deploy-job.json \
		| jq -r '.jobSummary.jobId')

	while :
	do
		sleep 10

		# Poll the deployment job status every 10 seconds until it's not pending
		# anymore
		STATUS=$(aws amplify get-job \
			--app-id $amplify_id \
			--branch-name $git_branch \
			--job-id $AMPLIFY_JOB_ID \
			| jq -r '.job.summary.status')

		if [ $STATUS != 'PENDING' ]; then
			break
		fi
	done

	printf "Amplify deployment status $STATUS\n"



}


web_to_amplify_function(){
	

	createl_zip
	publish_zip

}

web_to_amplify_function

echo "Done."
