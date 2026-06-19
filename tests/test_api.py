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
