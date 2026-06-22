"""Multiplayer game routes."""

from fastapi import APIRouter, HTTPException

from .models import CreateGameRequest, JoinGameRequest, MoveRequest
from .side import Side
from . import db, persistence
from .serializers import serialize_player, serialize_state


router = APIRouter(prefix="/games", tags=["multiplayer"])


@router.post("")
def create_game(req: CreateGameRequest):
    """Create a new game session."""
    game_id = db.create_game_session()
    return {
        "game_id": game_id,
        "status": "waiting_for_players",
        "min_players": req.min_players,
        "max_players": req.max_players,
    }


@router.post("/{game_id}/join")
def join_game(game_id: str, req: JoinGameRequest):
    """Join an existing game."""
    if game_id not in db.game_players:
        raise HTTPException(status_code=404, detail="Game not found.")
    
    if game_id in db.games:
        raise HTTPException(status_code=400, detail="Game already started. Cannot join.")
    
    player_id, token = db.add_player_to_game(game_id, req.player_name)
    
    return {
        "player_id": player_id,
        "player_name": req.player_name,
        "token": token,
        "players_count": len(db.game_players[game_id]),
    }


@router.post("/{game_id}/start")
def start_game(game_id: str):
    """Start the game with joined players."""
    if game_id not in db.game_players:
        raise HTTPException(status_code=404, detail="Game not found.")
    
    if game_id in db.games:
        raise HTTPException(status_code=400, detail="Game already started.")
    
    players_list = list(db.game_players[game_id].values())
    
    if len(players_list) < 2:
        raise HTTPException(
            status_code=400,
            detail=f"At least 2 players required. Current: {len(players_list)}"
        )
    
    game_engine = db.get_game_engine(game_id)
    state = game_engine.start_game(players_list)
    db.set_game(game_id, state)
    
    return {
        "game_id": game_id,
        "status": "started",
        "state": serialize_state(state),
    }


@router.get("/{game_id}/state")
def get_state(game_id: str):
    """Get the current game state."""
    state = db.get_game(game_id)
    if state is None:
        raise HTTPException(status_code=404, detail="Game not started or not found.")
    return serialize_state(state)


@router.get("/{game_id}/moves")
def get_moves(game_id: str):
    """Get valid moves for the current player."""
    state = db.get_game(game_id)
    if state is None:
        raise HTTPException(status_code=404, detail="Game not started or not found.")
    
    game_engine = db.get_game_engine(game_id)
    moves = game_engine.get_valid_moves(state)
    
    serialized = []
    for i, m in enumerate(moves):
        serialized.append({
            "index": i,
            "domino": m.domino.to_string(),
            "side": m.side.value if m.side is not None else None,
        })
    return {"moves": serialized}


@router.post("/{game_id}/move")
def play_move(game_id: str, req: MoveRequest):
    """Play a move in the game."""
    state = db.get_game(game_id)
    if state is None:
        raise HTTPException(status_code=404, detail="Game not started or not found.")
    
    current_player = state.players[state.current_player_index]
    
    # Validate that the request is from the current player
    if req.player_id != current_player.id:
        raise HTTPException(
            status_code=403,
            detail=f"It's not your turn. Current player: {current_player.name} (id={current_player.id})"
        )

    # Validate token
    if not db.verify_player_token(game_id, req.player_id, req.token):
        raise HTTPException(status_code=403, detail="Invalid or missing token for player.")
    
    game_engine = db.get_game_engine(game_id)
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
    db.set_game(game_id, state)
    
    # Save move to history
    persistence.save_move_history(
        game_id=game_id,
        player_id=req.player_id,
        move_index=req.move_index,
        move_data={"domino": chosen.domino.to_string(), "side": chosen.side.value if chosen.side else None}
    )
    
    winner = game_engine.check_win(state)
    result = {"state": serialize_state(state)}
    
    if winner:
        score = game_engine.calculate_scores(state, winner)
        result["winner"] = {"id": winner.id, "name": winner.name, "score": score}
    
    return result


@router.get("/{game_id}/players")
def list_players(game_id: str):
    """List all players in a game."""
    if game_id not in db.game_players:
        raise HTTPException(status_code=404, detail="Game not found.")
    
    players_list = list(db.game_players[game_id].values())
    return {"players": [serialize_player(p) for p in players_list]}
