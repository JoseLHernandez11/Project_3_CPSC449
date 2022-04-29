#!/bin/sh

curl -X GET -H 'Content-Type: application/json' localhost:9999/player_stats/ -d "{\"username\": \"$1\", \"user_id\": \"$2:-0\"}" | jq
