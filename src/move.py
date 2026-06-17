from src.domino import Domino
from src.side import Side

class Move:
    def __init__(self, player_id:int, domino: Domino, side: Side, is_pass: bool, is_draw: bool ):
        self.player_id = player_id
        self.domino = domino
        self.side = side
        self.is_pass = is_pass
        self.is_draw = is_draw
