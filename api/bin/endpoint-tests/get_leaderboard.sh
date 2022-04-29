#!/bin/sh

curl -X GET -H 'Content-Type: application/json' localhost:9999/leaderboard/ | jq
