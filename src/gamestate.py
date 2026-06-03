from board import Board
from pioche import Pioche
from player import Player
from gamestatus import GameStatus

class GameState:
    def __init__(self, board: Board, pioche: Pioche, players: list[Player], current_player_index: int, status: GameStatus, consecutive_passes: int):
        self.board = board
        self.pioche = pioche
        self.players = players
        self.current_player_index = current_player_index
        self.status = status
        self.consecutive_passes = consecutive_passes
