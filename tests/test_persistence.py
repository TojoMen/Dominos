"""Tests for SQLite persistence layer."""

import os
import sys
import json
import tempfile
import pytest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from src import persistence


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    yield db_path
    if os.path.exists(db_path):
        os.unlink(db_path)


def test_init_db(temp_db):
    """Test database initialization."""
    persistence.init_db(temp_db)
    assert os.path.exists(temp_db)


def test_save_and_load_game(temp_db):
    """Test saving and loading game state."""
    persistence.init_db(temp_db)
    
    game_id = "test_game_1"
    state = {"board": "0-1|1-2|2-3", "current_player": 0, "status": "in_progress"}
    
    persistence.save_game(game_id, state, temp_db)
    loaded = persistence.load_game(game_id, temp_db)
    
    assert loaded == state


def test_save_player_token(temp_db):
    """Test saving and loading player tokens."""
    persistence.init_db(temp_db)
    
    game_id = "test_game_2"
    player_id = "0"
    player_name = "Alice"
    token = "token_123"
    
    # First create a game
    persistence.save_game(game_id, {}, temp_db)
    
    # Then save player
    persistence.save_player_token(game_id, player_id, player_name, token, temp_db)
    
    # Verify
    assert persistence.verify_player_token(game_id, player_id, token, temp_db) == True
    assert persistence.verify_player_token(game_id, player_id, "wrong_token", temp_db) == False


def test_get_players_for_game(temp_db):
    """Test retrieving all players for a game."""
    persistence.init_db(temp_db)
    
    game_id = "test_game_3"
    persistence.save_game(game_id, {}, temp_db)
    
    persistence.save_player_token(game_id, "0", "Alice", "token_a", temp_db)
    persistence.save_player_token(game_id, "1", "Bob", "token_b", temp_db)
    
    players = persistence.get_players_for_game(game_id, temp_db)
    
    assert len(players) == 2
    assert players["0"]["name"] == "Alice"
    assert players["1"]["name"] == "Bob"


def test_save_move_history(temp_db):
    """Test saving move history."""
    persistence.init_db(temp_db)
    
    game_id = "test_game_4"
    persistence.save_game(game_id, {}, temp_db)
    
    move_data = {"domino": "1-2", "side": "right"}
    persistence.save_move_history(game_id, "0", 0, move_data, temp_db)
    
    # Verify by querying directly (no load function yet)
    import sqlite3
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM moves_history WHERE game_id = ?", (game_id,))
    count = cursor.fetchone()[0]
    conn.close()
    
    assert count == 1


def test_delete_game(temp_db):
    """Test deleting a game."""
    persistence.init_db(temp_db)
    
    game_id = "test_game_5"
    persistence.save_game(game_id, {"status": "active"}, temp_db)
    
    # Verify it exists
    assert persistence.load_game(game_id, temp_db) is not None
    
    # Delete
    persistence.delete_game(game_id, temp_db)
    
    # Verify it's gone
    assert persistence.load_game(game_id, temp_db) is None


def test_get_game_statistics(temp_db):
    """Test retrieving game statistics."""
    persistence.init_db(temp_db)
    
    game_id = "test_game_6"
    persistence.save_game(game_id, {}, temp_db)
    persistence.save_player_token(game_id, "0", "Alice", "token_a", temp_db)
    persistence.save_player_token(game_id, "1", "Bob", "token_b", temp_db)
    persistence.save_move_history(game_id, "0", 0, {"domino": "1-2"}, temp_db)
    persistence.save_move_history(game_id, "1", 1, {"domino": "2-3"}, temp_db)
    
    stats = persistence.get_game_statistics(game_id, temp_db)
    
    assert stats["game_id"] == game_id
    assert stats["num_players"] == 2
    assert stats["num_moves"] == 2


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
