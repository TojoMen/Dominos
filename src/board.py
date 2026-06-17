from src.domino import Domino
from src.pip_enum import Pip
from src.side import Side
from src.move import Move

class Board:
    def __init__(self):
        self.left_end: Pip | None = None
        self.right_end: Pip | None = None
        self.moves: list[Move] = []

    def update(self, domino, side:Side):
        if side == Side.LEFT:
            if domino.left_end == self.left_end:
                self.left_end = domino.right_end
                domino.inverser()
            else:
                self.left_end = domino.left_end
            self.moves.append(Move(0, domino, Side.LEFT, False, False))
        else:
            if domino.left_end == self.right_end:
                self.right_end = domino.right_end
            else:
                self.right_end = domino.left_end
                domino.inverser()
            self.moves.append(Move(0, domino, Side.RIGHT, False, False))

    def place(self, domino: Domino, side: Side):
        if len(self.moves) == 0:
            self.moves.append(Move(0,domino, Side.LEFT, False, False))
            self.left_end = domino.left_end
            self.right_end = domino.right_end
            return
        if side == Side.BOTH:
            # Déterministe pour l'API : choisir la gauche par défaut
            self.update(domino, Side.LEFT)
        if side == Side.RIGHT and domino.matches(self.right_end):
            self.update(domino, Side.RIGHT)
        elif side == Side.LEFT and domino.matches(self.left_end):
            self.update(domino, Side.LEFT)

    def affichage(self) -> str:
        jeu = ""
        print("longeur du board = " + str(len(self.moves)))
        for m in self.moves:
            if m.side == Side.LEFT :
                jeu = m.domino.to_string() +" "+ jeu
            else:
                jeu = jeu + " "  + m.domino.to_string() 
        return jeu