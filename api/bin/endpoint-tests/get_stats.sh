#!/bin/sh

curl -X GET -H 'Content-Type: application/json' localhost:5200/player_stats/ -d "{\"user_id\": \"$1\"| jq
