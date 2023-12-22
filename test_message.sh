#!/usr/bin/env sh

TOPIC=
MSG=

gcloud pubsub topics publish $TOPIC --message $MSG
