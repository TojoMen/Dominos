"""Pydantic models for API requests and responses."""

from pydantic import BaseModel
from typing import List, Optional


class CreateGameRequest(BaseModel):
    """Request to create a new game."""
    min_players: Optional[int] = 2
    max_players: Optional[int] = 3


class JoinGameRequest(BaseModel):
    """Request to join an existing game."""
    player_name: str


class MoveRequest(BaseModel):
    """Request to play a move."""
    move_index: int
    player_id: Optional[str] = None  # Required for multiplayer
    token: Optional[str] = None  # Required for multiplayer
    side: Optional[str] = None  # 'left' or 'right'


class StartRequest(BaseModel):
    """Legacy: Request to start game with specific player names."""
    player_names: Optional[List[str]] = None
