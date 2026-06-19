import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from fastapi.testclient import TestClient
from src import api

client = TestClient(api.app)


def setup_function():
    api.state = None
    api.players = []


def test_start_game_default():
    response = client.post("/start", json={})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "in_progress"
    assert len(data["players"]) == 3
    assert data["consecutive_passes"] == 0


def test_get_state_without_start():
    response = client.get("/state")
    assert response.status_code == 404


def test_get_moves_after_start():
    client.post("/start", json={})
    response = client.get("/moves")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data["moves"], list)


def test_play_move_invalid_index():
    client.post("/start", json={})
    response = client.post("/move", json={"move_index": 999})
    assert response.status_code == 400


def test_start_game_requires_at_least_two_players():
    response = client.post("/start", json={"player_names": ["Solo"]})
    assert response.status_code == 400
    assert response.json()["detail"] == "At least 2 players are required to start a game."


def test_join_returns_token_and_move_requires_token():
    # Create a new game then join two players
    response_game = client.post("/games", json={})
    assert response_game.status_code == 200
    game_id = response_game.json()["game_id"]

    response_a = client.post(f"/games/{game_id}/join", json={"player_name": "Alice"})
    assert response_a.status_code == 200
    token_a = response_a.json()["token"]
    player_id_a = response_a.json()["player_id"]

    response_b = client.post(f"/games/{game_id}/join", json={"player_name": "Bob"})
    assert response_b.status_code == 200
    token_b = response_b.json()["token"]
    player_id_b = response_b.json()["player_id"]

    response_start = client.post(f"/games/{game_id}/start", json={})
    assert response_start.status_code == 200

    # Play a move with missing token should fail
    current_state = client.get(f"/games/{game_id}/state").json()
    current_player_id = current_state["players"][current_state["current_player_index"]]["id"]
    response_invalid = client.post(
        f"/games/{game_id}/move",
        json={"player_id": current_player_id, "move_index": 0}
    )
    assert response_invalid.status_code == 403
    assert "Invalid or missing token" in response_invalid.json()["detail"]

    # Play a move with the valid token should either succeed or return a valid move response
    token = token_a if current_player_id == player_id_a else token_b
    response_valid = client.post(
        f"/games/{game_id}/move",
        json={"player_id": current_player_id, "token": token, "move_index": 0}
    )
    assert response_valid.status_code == 200
    assert "state" in response_valid.json()
