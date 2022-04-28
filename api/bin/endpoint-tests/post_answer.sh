#!/bin/sh

curl -X POST -H 'Content-Type: application/json' localhost:5100/answers/ -d "{\"word\": \"$1\"}"
