#!/bin/sh

curl -X GET -H 'Content-Type: application/json' localhost:5300/longest_streak/ | jq
