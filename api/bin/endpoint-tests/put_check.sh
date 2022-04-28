#!/bin/sh

curl -X PUT -H 'Content-Type: application/json' localhost:5100/check/ -d "{\"word\": \"$1\"}"
