from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict
from uuid import uuid4

from .gameengine import GameEngine
from .player import Player
from .move import Move
from .side import Side
from .gamestatus import GameStatus
from .gamestate import GameState

app = FastAPI(title="Dominos API - Multiplayer")

# Global game storage: game_id -> GameState
games: Dict[str, GameState] = {}
# Track players joining: game_id -> {player_id -> Player}
game_players: Dict[str, Dict[str, Player]] = {}
# Track player tokens: game_id -> {player_id -> token}
game_player_tokens: Dict[str, Dict[str, str]] = {}
# Track engine instances: game_id -> GameEngine
game_engines: Dict[str, GameEngine] = {}

engine = GameEngine()  # Default engine for backwards compatibility

# Legacy global variables for backwards compatibility
state = None
players = []


# ============= Request Models =============

class CreateGameRequest(BaseModel):
    """Request to create a new game"""
    min_players: Optional[int] = 2
    max_players: Optional[int] = 3


class JoinGameRequest(BaseModel):
    """Request to join an existing game"""
    player_name: str


class MoveRequest(BaseModel):
    """Request to play a move"""
    move_index: int
    player_id: Optional[str] = None  # Required for multiplayer
    token: Optional[str] = None  # Required for multiplayer
    side: Optional[str] = None  # 'left' or 'right'


class StartRequest(BaseModel):
    """Legacy: Request to start game with specific player names"""
    player_names: Optional[List[str]] = None


# ============= Serialization Functions =============

def serialize_player(p: Player) -> dict:
    return {
        "id": p.id,
        "name": p.name,
        "hand": [d.to_string() for d in p.hand.dominos],
        "score": p.score,
    }


def serialize_state(s: GameState) -> dict:
    return {
        "board": s.board.affichage(),
        "players": [serialize_player(p) for p in s.players],
        "current_player_index": s.current_player_index,
        "status": s.status.value,
        "consecutive_passes": s.consecutive_passes,
    }


# ============= NEW: Multiplayer Endpoints =============

@app.post("/games")
def create_game(req: CreateGameRequest):
    """
    Create a new game session.
    Returns game_id that other players can join.
    """
    game_id = str(uuid4())
    game_players[game_id] = {}
    game_player_tokens[game_id] = {}
    game_engines[game_id] = GameEngine()
    
    return {
        "game_id": game_id,
        "status": "waiting_for_players",
        "min_players": req.min_players,
        "max_players": req.max_players,
    }


@app.post("/games/{game_id}/join")
def join_game(game_id: str, req: JoinGameRequest):
    """
    Join an existing game.
    Returns player_id that will be used for all subsequent moves.
    """
    if game_id not in game_players:
        raise HTTPException(status_code=404, detail="Game not found.")
    
    if game_id in games:
        raise HTTPException(status_code=400, detail="Game already started. Cannot join.")
    
    player_id = str(len(game_players[game_id]))
    token = str(uuid4())
    player = Player(id=player_id, name=req.player_name)
    game_players[game_id][player_id] = player
    game_player_tokens[game_id][player_id] = token
    
    return {
        "player_id": player_id,
        "player_name": player.name,
        "token": token,
        "players_count": len(game_players[game_id]),
    }


@app.post("/games/{game_id}/start")
def start_game_multiplayer(game_id: str):
    """
    Start the game with joined players.
    Requires at least 2 players.
    """
    if game_id not in game_players:
        raise HTTPException(status_code=404, detail="Game not found.")
    
    if game_id in games:
        raise HTTPException(status_code=400, detail="Game already started.")
    
    players_list = list(game_players[game_id].values())
    
    if len(players_list) < 2:
        raise HTTPException(
            status_code=400,
            detail=f"At least 2 players required. Current: {len(players_list)}"
        )
    
    game_engine = game_engines[game_id]
    state = game_engine.start_game(players_list)
    games[game_id] = state
    
    return {
        "game_id": game_id,
        "status": "started",
        "state": serialize_state(state),
    }


@app.get("/games/{game_id}/state")
def get_state_multiplayer(game_id: str):
    """Get the current game state."""
    if game_id not in games:
        raise HTTPException(status_code=404, detail="Game not started or not found.")
    
    return serialize_state(games[game_id])


@app.get("/games/{game_id}/moves")
def get_moves_multiplayer(game_id: str):
    """Get valid moves for the current player."""
    if game_id not in games:
        raise HTTPException(status_code=404, detail="Game not started or not found.")
    
    state = games[game_id]
    game_engine = game_engines[game_id]
    moves = game_engine.get_valid_moves(state)
    
    serialized = []
    for i, m in enumerate(moves):
        serialized.append({
            "index": i,
            "domino": m.domino.to_string(),
            "side": m.side.value if m.side is not None else None,
        })
    return {"moves": serialized}


@app.post("/games/{game_id}/move")
def play_move_multiplayer(game_id: str, req: MoveRequest):
    """
    Play a move in the game.
    player_id must match the current player turn.
    """
    if game_id not in games:
        raise HTTPException(status_code=404, detail="Game not started or not found.")
    
    state = games[game_id]
    current_player = state.players[state.current_player_index]
    
    # Validate that the request is from the current player
    if req.player_id != current_player.id:
        raise HTTPException(
            status_code=403,
            detail=f"It's not your turn. Current player: {current_player.name} (id={current_player.id})"
        )

    valid_token = game_player_tokens.get(game_id, {}).get(req.player_id)
    if req.token is None or req.token != valid_token:
        raise HTTPException(status_code=403, detail="Invalid or missing token for player.")
    
    game_engine = game_engines[game_id]
    moves = game_engine.get_valid_moves(state)
    
    if req.move_index < 0 or req.move_index >= len(moves):
        raise HTTPException(status_code=400, detail="move_index out of range")
    
    chosen = moves[req.move_index]
    
    # Override side if provided
    if req.side:
        s = req.side.lower()
        if s == "left":
            chosen.side = Side.LEFT
        elif s == "right":
            chosen.side = Side.RIGHT
        else:
            raise HTTPException(status_code=400, detail="side must be 'left' or 'right'")
    
    state = game_engine.apply_move(state, chosen)
    games[game_id] = state
    
    winner = game_engine.check_win(state)
    result = {"state": serialize_state(state)}
    
    if winner:
        score = game_engine.calculate_scores(state, winner)
        result["winner"] = {"id": winner.id, "name": winner.name, "score": score}
    
    return result


@app.get("/games/{game_id}/players")
def list_players_multiplayer(game_id: str):
    """List all players in a game."""
    if game_id not in game_players:
        raise HTTPException(status_code=404, detail="Game not found.")
    
    players_list = list(game_players[game_id].values())
    return {"players": [serialize_player(p) for p in players_list]}


# ============= LEGACY: Single-Game Endpoints (for backwards compatibility) =============

@app.post("/start")
def start_game(req: StartRequest):
    global players, state
    names = req.player_names or ["Tojo", "Rindra", "Dada"]
    if len(names) < 2:
        raise HTTPException(status_code=400, detail="At least 2 players are required to start a game.")
    players = [Player(id=str(i), name=name) for i, name in enumerate(names)]
    state = engine.start_game(players)
    return serialize_state(state)


@app.get("/state")
def get_state():
    if state is None:
        raise HTTPException(status_code=404, detail="No active game. POST /start to create one.")
    return serialize_state(state)


@app.get("/moves")
def get_moves():
    if state is None:
        raise HTTPException(status_code=404, detail="No active game.")
    moves = engine.get_valid_moves(state)
    serialized = []
    for i, m in enumerate(moves):
        serialized.append({
            "index": i,
            "domino": m.domino.to_string(),
            "side": m.side.value if m.side is not None else None,
        })
    return {"moves": serialized}


@app.post("/move")
def play_move(req: MoveRequest):
    global state
    if state is None:
        raise HTTPException(status_code=404, detail="No active game.")
    moves = engine.get_valid_moves(state)
    if req.move_index < 0 or req.move_index >= len(moves):
        raise HTTPException(status_code=400, detail="move_index out of range")
    chosen = moves[req.move_index]
    # override side if provided
    if req.side:
        s = req.side.lower()
        if s == "left":
            chosen.side = Side.LEFT
        elif s == "right":
            chosen.side = Side.RIGHT
        else:
            raise HTTPException(status_code=400, detail="side must be 'left' or 'right'")

    state = engine.apply_move(state, chosen)
    winner = engine.check_win(state)
    result = {"state": serialize_state(state)}
    if winner:
        score = engine.calculate_scores(state, winner)
        result["winner"] = {"id": winner.id, "name": winner.name, "score": score}
    return result


@app.get("/players")
def list_players():
    if not players:
        raise HTTPException(status_code=404, detail="No players configured. POST /start to create players.")
    return {"players": [serialize_player(p) for p in players]}
