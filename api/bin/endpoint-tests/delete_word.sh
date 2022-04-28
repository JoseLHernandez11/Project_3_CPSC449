#!/bin/sh

curl -X DELETE -H 'Content-Type: application/json' localhost:5000/words/ -d "{\"word\": \"$1\"}"
