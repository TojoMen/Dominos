"""Serialization functions to convert objects to JSON-safe dicts."""

from .player import Player
from .gamestate import GameState


def serialize_player(p: Player) -> dict:
    """Convert a Player object to a dict."""
    return {
        "id": p.id,
        "name": p.name,
        "hand": [d.to_string() for d in p.hand.dominos],
        "score": p.score,
    }


def serialize_state(s: GameState) -> dict:
    """Convert a GameState object to a dict."""
    return {
        "board": s.board.affichage(),
        "players": [serialize_player(p) for p in s.players],
        "current_player_index": s.current_player_index,
        "status": s.status.value,
        "consecutive_passes": s.consecutive_passes,
    }
