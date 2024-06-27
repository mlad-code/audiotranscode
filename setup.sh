#!/usr/bin/env sh

PROJECTID=
PROJECTNUM=
TOPIC=
ENDPOINT=
LOCATION=
DEIDENTIFY_TEMPLATE_NAME=
INSPECT_TEMPLATE_NAME=

#Create the Cloud Run
gcloud builds submit --tag gcr.io/$PROJECTID/transcoder
gcloud run deploy pubsub-transcoder --image gcr.io/$PROJECTID/transcoder  --set-env-vars PROJECT_ID=$PROJECTID,LOCATION=$LOCATION,DTN=$DEIDENTIFY_TEMPLATE_NAME,ITN=$INSPECT_TEMPLATE_NAME --concurrency=1 --cpu=2 --memory=1Gi --min-instances=1 --max-instances=500 --no-cpu-throttling  --no-allow-unauthenticated 

#Create the service account and allow authentication for that account only
gcloud iam service-accounts create cloud-run-pubsub-invoker --display-name "Cloud Run Pub/Sub Invoker"
gcloud run services add-iam-policy-binding pubsub-transcoder --member=serviceAccount:cloud-run-pubsub-invoker@$PROJECTID.iam.gserviceaccount.com --role=roles/run.invoker
gcloud projects add-iam-policy-binding $PROJECTID  --member=serviceAccount:service-$PROJECTNUM@gcp-sa-pubsub.iam.gserviceaccount.com --role=roles/iam.serviceAccountTokenCreator

#create subscription to topic
gcloud pubsub subscriptions create transcoder --topic $TOPIC --ack-deadline=600  --push-endpoint=$ENDPOINT  --push-auth-service-account=cloud-run-pubsub-invoker@$PROJECTID.iam.gserviceaccount.com
