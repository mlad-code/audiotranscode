#!/bin/sh

gsutil cp "gs://$GCS_BUCKET/$GCS_PATH/$GCS_FILE" "/tmp/src.wav"
ffmpeg -i /tmp/src.wav -acodec g723_1 -ac 1 /tmp/output.wav
gsutil cp "/tmp/output.wav" "gs://hqyconverted/$GCS_PATH/$GCS_FILE"
