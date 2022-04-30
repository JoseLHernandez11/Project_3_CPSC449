#!/bin/sh

curl -X POST -H 'Content-Type: application/json' localhost:5200/game_finished/ -d "{\user_id\": \"$1\", \"game_id\": \"$2\", \"number_of_guesses\": \"$3\", \"won\": \"$4\"}"| jq
