import base64
import re

from flask import Flask, request


app = Flask(__name__)

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
    print(f"Hello bucket {bucket} from {msg}!")
    print(f"Hello path {path} from {msg}!")
    print(f"Hello file {file} from {msg}!")

    return ("", 204)


def parse_gs_url(gs_url):
  """Parses a fully qualified gs url and separates it into bucket name, path and filename.

  Args:
    gs_url: A fully qualified gs url.

  Returns:
    A tuple containing the bucket name, path and filename.
  """

  match = re.match('gs://([^/]*)/(.*?)/(.*)', gs_url)
  if match:
    return match.groups()
  else:
    return None

