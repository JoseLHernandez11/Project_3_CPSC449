#!/bin/sh

curl -X PUT -H 'Content-Type: application/json' localhost:5000/validate/ -d "{\"word\": \"$1\"}"
