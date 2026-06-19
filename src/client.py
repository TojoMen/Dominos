#!/usr/bin/env python3
"""Simple CLI client for Dominos API.

Usage examples:
  python3 src/client.py create --server http://127.0.0.1:8000
  python3 src/client.py join --server http://127.0.0.1:8000 --game GAME_ID --name Alice
  python3 src/client.py start --server http://127.0.0.1:8000 --game GAME_ID
  python3 src/client.py state --server http://127.0.0.1:8000 --game GAME_ID
  python3 src/client.py moves --server http://127.0.0.1:8000 --game GAME_ID
  python3 src/client.py move --server http://127.0.0.1:8000 --game GAME_ID --player PLAYER_ID --token TOKEN --index 0
  python3 src/client.py play-e2e --server http://127.0.0.1:8000
"""

import argparse
import sys
import httpx
import time
import os
import json
from pathlib import Path

DEFAULT_SERVER = "http://127.0.0.1:8000"


def create_game(server: str):
    r = httpx.post(f"{server}/games", json={})
    r.raise_for_status()
    print(r.json())
    return r.json()


def join_game(server: str, game_id: str, name: str):
    r = httpx.post(f"{server}/games/{game_id}/join", json={"player_name": name})
    r.raise_for_status()
    resp = r.json()
    print(resp)
    # save credentials locally for convenience
    try:
        save_credentials(game_id, resp["player_id"], resp["token"])
        print(f"Saved credentials to {CONFIG_FILE}")
    except Exception:
        pass
    return resp


def start_game(server: str, game_id: str):
    r = httpx.post(f"{server}/games/{game_id}/start")
    r.raise_for_status()
    print(r.json())
    return r.json()


def get_state(server: str, game_id: str):
    r = httpx.get(f"{server}/games/{game_id}/state")
    r.raise_for_status()
    print(r.json())
    return r.json()


def get_moves(server: str, game_id: str):
    r = httpx.get(f"{server}/games/{game_id}/moves")
    r.raise_for_status()
    print(r.json())
    return r.json()


def play_move(server: str, game_id: str, player_id: str, token: str, index: int, side: str | None = None):
    payload = {"player_id": player_id, "token": token, "move_index": index}
    if side:
        payload["side"] = side
    r = httpx.post(f"{server}/games/{game_id}/move", json=payload)
    r.raise_for_status()
    print(r.json())
    return r.json()


def play_e2e(server: str):
    print("Creating game...")
    g = create_game(server)
    game_id = g["game_id"]
    print("Joining Alice...")
    a = join_game(server, game_id, "Alice")
    print("Joining Bob...")
    b = join_game(server, game_id, "Bob")
    print("Starting game...")
    start_game(server, game_id)
    time.sleep(0.2)
    state = get_state(server, game_id)
    current_index = state["current_player_index"]
    current_player = state["players"][current_index]
    player_id = current_player["id"]
    token = a["token"] if player_id == a["player_id"] else b["token"]
    print(f"Playing move as player {player_id} (token hidden)")
    moves = get_moves(server, game_id)["moves"]
    if not moves:
        print("No moves available for current player")
        return
    play_move(server, game_id, player_id, token, 0)


# Simple local credential storage (~/.dominos/credentials.json)
CONFIG_DIR = Path.home() / ".dominos"
CONFIG_FILE = CONFIG_DIR / "credentials.json"


def _load_all_credentials() -> dict:
    if not CONFIG_FILE.exists():
        return {}
    try:
        with CONFIG_FILE.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _save_all_credentials(data: dict):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with CONFIG_FILE.open("w", encoding="utf-8") as f:
        json.dump(data, f)


def save_credentials(game_id: str, player_id: str, token: str):
    data = _load_all_credentials()
    data[str(game_id)] = {"player_id": player_id, "token": token}
    _save_all_credentials(data)


def load_credentials(game_id: str):
    data = _load_all_credentials()
    return data.get(str(game_id))


def main(argv: list[str]):
    parser = argparse.ArgumentParser(prog="dominos-client")
    sub = parser.add_subparsers(dest="cmd")

    p_create = sub.add_parser("create")
    p_create.add_argument("--server", default=DEFAULT_SERVER)

    p_join = sub.add_parser("join")
    p_join.add_argument("--server", default=DEFAULT_SERVER)
    p_join.add_argument("--game", required=True)
    p_join.add_argument("--name", required=True)

    p_start = sub.add_parser("start")
    p_start.add_argument("--server", default=DEFAULT_SERVER)
    p_start.add_argument("--game", required=True)

    p_state = sub.add_parser("state")
    p_state.add_argument("--server", default=DEFAULT_SERVER)
    p_state.add_argument("--game", required=True)

    p_moves = sub.add_parser("moves")
    p_moves.add_argument("--server", default=DEFAULT_SERVER)
    p_moves.add_argument("--game", required=True)

    p_move = sub.add_parser("move")
    p_move.add_argument("--server", default=DEFAULT_SERVER)
    p_move.add_argument("--game", required=True)
    p_move.add_argument("--player", required=True)
    p_move.add_argument("--token", required=False)
    p_move.add_argument("--index", type=int, required=True)
    p_move.add_argument("--side", choices=["left","right"], required=False)

    p_e2e = sub.add_parser("play-e2e")
    p_e2e.add_argument("--server", default=DEFAULT_SERVER)

    args = parser.parse_args(argv)

    try:
        if args.cmd == "create":
            create_game(args.server)
        elif args.cmd == "join":
            join_game(args.server, args.game, args.name)
        elif args.cmd == "start":
            start_game(args.server, args.game)
        elif args.cmd == "state":
            get_state(args.server, args.game)
        elif args.cmd == "moves":
            get_moves(args.server, args.game)
        elif args.cmd == "move":
            token = args.token
            if token is None:
                # try load from saved credentials
                creds = load_credentials(args.game)
                if creds and creds.get("player_id") == args.player:
                    token = creds.get("token")
                    print("Loaded token from local credentials")
            if token is None:
                print("No token provided and none found in local credentials. Use --token or join first.")
                sys.exit(1)
            play_move(args.server, args.game, args.player, token, args.index, args.side)
        elif args.cmd == "play-e2e":
            play_e2e(args.server)
        else:
            parser.print_help()
    except httpx.HTTPStatusError as e:
        print("Request failed:", e.response.status_code, e.response.text)
        sys.exit(1)
    except Exception as e:
        print("Error:", e)
        sys.exit(1)


if __name__ == "__main__":
    main(sys.argv[1:])
