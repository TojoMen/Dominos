"""Legacy single-game routes for backwards compatibility."""

from fastapi import APIRouter, HTTPException

from .models import StartRequest, MoveRequest
from .side import Side
from . import db
from .serializers import serialize_player, serialize_state


router = APIRouter(tags=["legacy"])


@router.post("/start")
def start_game(req: StartRequest):
    """Legacy endpoint: create and start a single-game session."""
    names = req.player_names or ["Tojo", "Rindra", "Dada"]
    if len(names) < 2:
        raise HTTPException(status_code=400, detail="At least 2 players are required to start a game.")
    
    db.players = []
    from .player import Player
    db.players = [Player(id=str(i), name=name) for i, name in enumerate(names)]
    db.state = db.engine.start_game(db.players)
    return serialize_state(db.state)


@router.get("/state")
def get_state():
    """Legacy endpoint: get the last started game state."""
    if db.state is None:
        raise HTTPException(status_code=404, detail="No active game. POST /start to create one.")
    return serialize_state(db.state)


@router.get("/moves")
def get_moves():
    """Legacy endpoint: get moves for the last started game."""
    if db.state is None:
        raise HTTPException(status_code=404, detail="No active game.")
    moves = db.engine.get_valid_moves(db.state)
    serialized = []
    for i, m in enumerate(moves):
        serialized.append({
            "index": i,
            "domino": m.domino.to_string(),
            "side": m.side.value if m.side is not None else None,
        })
    return {"moves": serialized}


@router.post("/move")
def play_move(req: MoveRequest):
    """Legacy endpoint: play a move in the last started game."""
    if db.state is None:
        raise HTTPException(status_code=404, detail="No active game.")
    moves = db.engine.get_valid_moves(db.state)
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

    db.state = db.engine.apply_move(db.state, chosen)
    winner = db.engine.check_win(db.state)
    result = {"state": serialize_state(db.state)}
    if winner:
        score = db.engine.calculate_scores(db.state, winner)
        result["winner"] = {"id": winner.id, "name": winner.name, "score": score}
    return result


@router.get("/players")
def list_players():
    """Legacy endpoint: list players in the last started game."""
    if not db.players:
        raise HTTPException(status_code=404, detail="No players configured. POST /start to create players.")
    return {"players": [serialize_player(p) for p in db.players]}
