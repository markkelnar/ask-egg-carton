#!/bin/bash

ID=`python -mjson.tool .ask/ask-states.json | python -c 'import sys, json; print json.load(sys.stdin)["profiles"]["default"]["skillId"]'`
DATA=`cat skill-package/interactionModels/custom/en-US.json`
ask smapi set-interaction-model -s "$ID" --stage development -l en-US --interaction-model="$DATA"

