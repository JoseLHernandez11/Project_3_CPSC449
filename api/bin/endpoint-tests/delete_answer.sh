#!/bin/sh

curl -X DELETE -H 'Content-Type: application/json' localhost:5100/answers/ -d "{\"word\": \"$1\"}"
