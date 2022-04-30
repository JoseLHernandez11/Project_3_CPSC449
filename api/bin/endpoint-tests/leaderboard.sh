#!/bin/sh

curl -X GET -H 'Content-Type: application/json' localhost:5200/leaderboard/ | jq
