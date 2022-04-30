#!/bin/sh

curl -X GET -H 'Content-Type: application/json' localhost:5200/maximum_streak/ | jq
