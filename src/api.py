from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional

from .gameengine import GameEngine
from .player import Player
from .move import Move
from .side import Side
from .gamestatus import GameStatus
from .gamestate import GameState

app = FastAPI(title="Dominos API")

# Global in-memory game objects (simple demo)
engine: GameEngine = GameEngine()
players: List[Player] = []
state: Optional[GameState] = None


class StartRequest(BaseModel):
    player_names: Optional[List[str]] = None


class MoveRequest(BaseModel):
    move_index: int
    side: Optional[str] = None  # 'left' or 'right'


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


@app.post("/start")
def start_game(req: StartRequest):
    global players, state
    names = req.player_names or ["Tojo", "Rindra", "Dada"]
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
