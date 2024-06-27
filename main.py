import base64
import os
import re
import subprocess
from datetime import datetime
import requests
from google.cloud import storage
from google.cloud import contactcenterinsights_v1

from flask import Flask, request

app = Flask(__name__)

# url = "https://contactcenterinsights.googleapis.com/v1/projects/" + project_id + "/locations/" + location + "/conversations:upload"
# UPDATE WITH YOUR PROJECT INFO
project_id = os.getenv("PROJECT_ID")
location = os.getenv("LOCATION")
deidentify_template_name = os.getenv("DTN")
inspect_template_name = os.getenv("ITN")

# Initialize the Contact Center AI Insights client

# Initialize the Contact Center AI Insights client
client = contactcenterinsights_v1.ContactCenterInsightsClient()

@app.route("/", methods=["POST"])
def index():
    """Receive and parse Pub/Sub messages."""
    envelope = request.get_json()
    if not envelope:
        msg = "no Pub/Sub message received"
        print(f"error: {msg}")
        return f"Bad Request: {msg}", 400

    if not isinstance(envelope, dict) or "message" not in envelope:
        msg = "invalid Pub/Sub message format"
        print(f"error: {msg}")
        return f"Bad Request: {msg}", 400

    pubsub_message = envelope["message"]

    msg = "path"
    if isinstance(pubsub_message, dict) and "data" in pubsub_message:
        msg = base64.b64decode(pubsub_message["data"]).decode("utf-8").strip()

    (bucket, path, file) = parse_gs_url(msg) 

    # Download the audio file from Google Cloud Storage
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket)
    blob = bucket.blob(f"{path}/{file}")
    blob.download_to_filename('/tmp/src.wav')

    # Convert the audio file to the desired format using ffmpeg
    subprocess.call(['/opt/build/bin/ffmpeg', '-i', '/tmp/src.wav', '-ac', '2', '-y', "/tmp/output.wav"])

    # Upload the converted file to a new Google Cloud Storage bucket
    bucket = storage_client.bucket("hqyconverted")
    blob = bucket.blob(f"{path}/{file}")
    blob.upload_from_filename('/tmp/output.wav')

    # Construct the request body
    # data = {
    #     "conversation": {
    #         "data_source": {
    #             "gcs_source": {"audio_uri": f"gs://hqyconverted/{path}/{file}"}
    #         }
    #     },
    #     "agentId": "AGENT",
    #     "callMetadata": {
    #         "agentChannel": 1,
    #         "customerChannel": 2
    #     },
    #     "redaction_config": {
    #         "deidentify_template": deidentify_template_name,
    #         "inspect_template": inspect_template_name
    #     }
    # }

    # Send the request to Contact Center AI Insights
    try:
        response = client.upload_conversation(
            parent=f"projects/{project_id}/locations/{location}",
            conversation=contactcenterinsights_v1.Conversation(
                data_source=contactcenterinsights_v1.DataSource(
                    gcs_source=contactcenterinsights_v1.GcsSource(
                        audio_uri=f"gs://hqyconverted/{path}/{file}"
                    )
                ),
                agent_id="AGENT",
                call_metadata=contactcenterinsights_v1.CallMetadata(
                    agent_channel=1, customer_channel=2
                ),
                redaction_config=contactcenterinsights_v1.RedactionConfig(
                    deidentify_template=deidentify_template_name,
                    inspect_template=inspect_template_name
                )
            )
        )
        print("Status Code:", response.status_code)
        print("JSON Response:", response.json())
    except requests.exceptions.RequestException as e:
        print(f"Error uploading conversation: {e}")

    # Clean up temporary files
    try:
        os.remove('/tmp/src.wav')
        os.remove('/tmp/output.wav')
    except FileNotFoundError:
        pass  # Ignore if files don't exist
    return ("", 204)


def parse_gs_url(gs_url):
  """Parses a fully qualified gs url and separates it into bucket name, path and filename.

  Args:
    gs_url: A fully qualified gs url.

  Returns:
    A tuple containing the bucket name, path and filename.
  """

  match = re.match('gs://([^/]*)/(.*)/(.*)', gs_url)
  if match:
    return match.groups()
  else:
    return None

