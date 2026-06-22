"""Global database/state management for games."""

from typing import Dict, Optional
from uuid import uuid4

from .gameengine import GameEngine
from .player import Player
from .gamestate import GameState


# Global game storage: game_id -> GameState
games: Dict[str, GameState] = {}

# Track players joining: game_id -> {player_id -> Player}
game_players: Dict[str, Dict[str, Player]] = {}

# Track player tokens: game_id -> {player_id -> token}
game_player_tokens: Dict[str, Dict[str, str]] = {}

# Track engine instances: game_id -> GameEngine
game_engines: Dict[str, GameEngine] = {}

# Default engine for backwards compatibility
engine = GameEngine()

# Legacy global variables for backwards compatibility
state: Optional[GameState] = None
players: list[Player] = []


def create_game_session() -> str:
    """Create a new game session and return game_id."""
    game_id = str(uuid4())
    game_players[game_id] = {}
    game_player_tokens[game_id] = {}
    game_engines[game_id] = GameEngine()
    return game_id


def add_player_to_game(game_id: str, player_name: str) -> tuple[str, str]:
    """
    Add a player to a game and return (player_id, token).
    """
    if game_id not in game_players:
        raise ValueError(f"Game {game_id} not found")
    
    player_id = str(len(game_players[game_id]))
    token = str(uuid4())
    player = Player(id=player_id, name=player_name)
    
    game_players[game_id][player_id] = player
    game_player_tokens[game_id][player_id] = token
    
    return player_id, token


def get_game(game_id: str) -> Optional[GameState]:
    """Get a game state by ID."""
    return games.get(game_id)


def set_game(game_id: str, state: GameState):
    """Store a game state."""
    games[game_id] = state


def get_game_engine(game_id: str) -> Optional[GameEngine]:
    """Get the engine for a game."""
    return game_engines.get(game_id)


def get_game_players(game_id: str) -> Dict[str, Player]:
    """Get all players in a game."""
    return game_players.get(game_id, {})


def get_player_token(game_id: str, player_id: str) -> Optional[str]:
    """Get the token for a player in a game."""
    return game_player_tokens.get(game_id, {}).get(player_id)


def verify_player_token(game_id: str, player_id: str, token: str) -> bool:
    """Verify that a token is valid for a player in a game."""
    valid_token = get_player_token(game_id, player_id)
    return valid_token is not None and valid_token == token
