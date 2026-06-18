import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from src.gameengine import GameEngine
from src.player import Player
from src.hand import Hand
from src.board import Board
from src.pioche import Pioche
from src.domino import Domino
from src.gamestate import GameState
from src.gamestatus import GameStatus
from src.pip_enum import Pip


def test_check_win_when_player_has_no_dominos():
    players = [Player(id="0", name="A"), Player(id="1", name="B"), Player(id="2", name="C")]
    players[0].hand = Hand([])
    players[1].hand = Hand([Domino(Pip.ONE, Pip.ONE)])
    players[2].hand = Hand([Domino(Pip.TWO, Pip.TWO)])
    state = GameState(board=Board(), pioche=Pioche([]), players=players, current_player_index=0, status=GameStatus.IN_PROGRESS, consecutive_passes=0)

    engine = GameEngine()
    winner = engine.check_win(state)

    assert winner is players[0]
    assert state.status == GameStatus.FINISHED


def test_calculate_scores_adds_points_to_winner():
    players = [Player(id="0", name="A"), Player(id="1", name="B"), Player(id="2", name="C")]
    players[0].hand = Hand([])
    players[1].hand = Hand([Domino(Pip.ONE, Pip.ONE)])
    players[2].hand = Hand([Domino(Pip.TWO, Pip.THREE)])
    state = GameState(board=Board(), pioche=Pioche([]), players=players, current_player_index=0, status=GameStatus.IN_PROGRESS, consecutive_passes=0)

    engine = GameEngine()
    score = engine.calculate_scores(state, players[0])

    assert score == players[0].score
    assert score == players[1].hand.total() + players[2].hand.total()
