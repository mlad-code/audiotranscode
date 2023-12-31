import base64
import re
import subprocess
import json
from datetime import datetime
import requests

from flask import Flask, request


app = Flask(__name__)

# UPDATE WITH YOUR PROJECT INFO
project_id = "project-2-405406"
location = "us-central1"
url = "https://contactcenterinsights.googleapis.com/v1/projects/"+project_id+"/locations/"+location+"/conversations:upload"
deIdentifyTemplate = "projects/project-2-405406/locations/us-central1/deidentifyTemplates/V5_DeIdentify_Template"
inspectTemplate = "projects/project-2-405406/locations/us-central1/inspectTemplates/V5_Inspection_Template"

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
    subprocess.call(['gsutil','cp', f"gs://{bucket}/{path}/{file}", '/tmp/src.wav'])
    subprocess.call(['/opt/build/bin/ffmpeg', '-i', '/tmp/src.wav', '-ac', '2', '/tmp/output.wav'])
    subprocess.call(['gsutil','cp', '/tmp/output.wav', f"gs://hqyconverted/{path}/{file}"])
    data = f""" {{ 
        ""conversation"": {{ 
            ""data_source"": {{ 
            ""gcs_source"": {{ ""audio_uri"": gs://hqyconverted/{path}/{file} }}
            }}
        }},
        ""redaction_config"": {{
                ""deidentify_template"": {{deIdentifyTemplate}},
                ""inspect_template"": {{inspectTemplate}}        
        }}
    }} 
"""
    atoken = subprocess.run(['gcloud','auth','print-access-token'], capture_output=True, text=True)
    headers = {'Content-Type':'application/json; charset=utf-8', 'Authorization':'Bearer {}'.format(atoken)}
    # transcribe, redact and upload each file
    response = requests.post(url, headers=headers, json=data)
    print("Status Code", response.status_code)
    print("JSON Response ", response.json())


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

