#!/usr/bin/env bash
# Mini end-to-end test using curl + jq for the Dominos API
# Usage: SERVER=http://localhost:8000 ./scripts/e2e_curl.sh
# Requires: jq (for JSON parsing)

set -euo pipefail
: ${SERVER:=http://127.0.0.1:8000}

echo "Server: ${SERVER}"

# 1) Create a game
echo "\n1) Create game"
resp=$(curl -s -X POST "${SERVER}/games" -H "Content-Type: application/json" -d '{}')
echo "Response: $resp"
game_id=$(echo "$resp" | jq -r .game_id)
if [ -z "$game_id" ] || [ "$game_id" = "null" ]; then
  echo "Failed to create game"
  exit 1
fi

echo "game_id=$game_id"

# 2) Two players join (Alice and Bob)
echo "\n2) Players join"
resp_a=$(curl -s -X POST "${SERVER}/games/${game_id}/join" -H "Content-Type: application/json" -d '{"player_name":"Alice"}')
player_a_id=$(echo "$resp_a" | jq -r .player_id)
player_a_token=$(echo "$resp_a" | jq -r .token)
echo "Alice joined with player_id=$player_a_id token=$player_a_token"

resp_b=$(curl -s -X POST "${SERVER}/games/${game_id}/join" -H "Content-Type: application/json" -d '{"player_name":"Bob"}')
player_b_id=$(echo "$resp_b" | jq -r .player_id)
player_b_token=$(echo "$resp_b" | jq -r .token)
echo "Bob joined with player_id=$player_b_id token=$player_b_token"

# 3) Start the game
echo "\n3) Start game"
resp_start=$(curl -s -X POST "${SERVER}/games/${game_id}/start" -H "Content-Type: application/json")
echo "Start response: $resp_start"

# 4) Get moves for current player
echo "\n4) Get moves"
resp_moves=$(curl -s "${SERVER}/games/${game_id}/moves")
echo "Moves: $resp_moves"

# Pick a move index 0 if available, else exit
moves_count=$(echo "$resp_moves" | jq '.moves | length')
if [ "$moves_count" -eq 0 ]; then
  echo "No moves available for current player"
  exit 0
fi

# 5) Play move as current player
# Determine current player id from state
state=$(curl -s "${SERVER}/games/${game_id}/state")
current_index=$(echo "$state" | jq -r '.current_player_index')
current_player_id=$(echo "$state" | jq -r ".players[$current_index].id")
echo "Current player id: $current_player_id"

if [ "$current_player_id" = "$player_a_id" ]; then
  current_player_token="$player_a_token"
else
  current_player_token="$player_b_token"
fi

echo "Current player token: $current_player_token"

# Play move 0
echo "\n5) Play move index 0 as player $current_player_id"
resp_move=$(curl -s -X POST "${SERVER}/games/${game_id}/move" -H "Content-Type: application/json" -d "{\"player_id\": \"${current_player_id}\", \"token\": \"${current_player_token}\", \"move_index\": 0}")
echo "Move response: $resp_move"

# 6) Final state
echo "\n6) Final state"
final_state=$(curl -s "${SERVER}/games/${game_id}/state")
echo "$final_state" | jq

echo "\nE2E script finished. If you run against ngrok, set SERVER to the ngrok URL (e.g. https://abcd.ngrok.io)"
