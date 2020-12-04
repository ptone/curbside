source env.bash
gcloud config set project $GOOGLE_CLOUD_PROJECT
gcloud services enable run.googleapis.com   

# Create an App Engine app - this will not be used, but is required to set up Firestore database
gcloud app create --region=us-central --project $GOOGLE_CLOUD_PROJECT

# Add Firebase to the Cloud Projects
firebase projects:addfirebase $GOOGLE_CLOUD_PROJECT

# Create the Firestore database
gcloud firestore databases create --project $GOOGLE_CLOUD_PROJECT --region us-central

# Deploy the Firestore Rules and Indexes
firebase deploy --only firestore


# Create a Firebase webapp so we can retrieve configuration
firebase apps:create web --project $GOOGLE_CLOUD_PROJECT curbside

# set the frontend firebase config file
firebase apps:sdkconfig web --project $GOOGLE_CLOUD_PROJECT \
 | sed -n '/{/,/}/ { //d; /^\s*$/!p }' \
 | sed -i -e '/fromfirebase/{r /dev/stdin' -e 'd;}' \
 web/src/fbconfig.js

# Create a service identity for the webhook
gcloud iam service-accounts create curbside-agent

# Grant permission to that identity to access the database
gcloud projects add-iam-policy-binding $GOOGLE_CLOUD_PROJECT \
--member serviceAccount:curbside-agent@$GOOGLE_CLOUD_PROJECT.iam.gserviceaccount.com \
--role roles/datastore.user



# Build the container image
docker build -t gcr.io/$GOOGLE_CLOUD_PROJECT/app . 

# Push the container to the project registry
docker push gcr.io/$GOOGLE_CLOUD_PROJECT/app

# Deploy the service
gcloud run deploy app \
--project $GOOGLE_CLOUD_PROJECT \
--image gcr.io/$GOOGLE_CLOUD_PROJECT/app \
--region us-central1 \
--allow-unauthenticated \
--platform managed \
--service-account curbside-agent@$GOOGLE_CLOUD_PROJECT.iam.gserviceaccount.com \
--set-env-vars=TWILIO_ACCOUNT_SID=$TWILIO_ACCOUNT_SID,TWILIO_AUTH_TOKEN=$TWILIO_AUTH_TOKEN,GOOGLE_CLOUD_PROJECT=$GOOGLE_CLOUD_PROJECT
pip3 install -r requirements.txt
python3 update_deploy.py 

cloudshell edit docs/install_complete.md 

URL=`gcloud run services describe app --platform managed --region us-central1 --format='value(status.url)'`

gcloud run services describe app --platform managed --region us-central1 --format='value(status.url)'
clear
echo "Install Completed"
echo "Please open https://console.firebase.google.com/u/0/project/$GOOGLE_CLOUD_PROJECT/authentication/providers"