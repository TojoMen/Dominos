from domino import Domino
from pip_enum import Pip
from side import Side
from move import Move

class Board:
    def __init__(self):
        self.left_end: Pip | None = None
        self.right_end: Pip | None = None
        self.dom: list[Move] = []

    def update(self, domino, side:Side):
        if side == Side.LEFT:
            if domino.left_end == self.left_end:
                self.left_end = domino.right_end
                domino.inverser()
            else:
                self.left_end = domino.left_end
            self.dom.append(Move(0, domino, Side.LEFT, False, False))
        else:
            if domino.left_end == self.right_end:
                self.right_end = domino.right_end
            else:
                self.right_end = domino.left_end
                domino.inverser()
            self.dom.append(Move(0, domino, Side.RIGHT, False, False))

    def place(self, domino: Domino, side: Side):
        if len(self.dom) == 0:
            self.dom.append(Move(0,domino, Side.LEFT, False, False))
            self.left_end = domino.left_end
            self.right_end = domino.right_end
            return
        if side == Side.BOTH:
            choix = input("choisir un coté :")
            if choix == "left":
                self.update(domino, Side.LEFT)
            else:
                self.update(domino, Side.RIGHT)
        if side == Side.RIGHT and domino.matches(self.right_end):
            self.update(domino, Side.RIGHT)
        elif side == Side.LEFT and domino.matches(self.left_end):
            self.update(domino, Side.LEFT)

    def affichage(self) -> str:
        jeu = ""
        print("longeur du board = " + str(len(self.dom)))
        for m in self.dom:
            if m.side == Side.LEFT :
                jeu = m.domino.to_string() +" "+ jeu
            else:
                jeu = jeu + " "  + m.domino.to_string() 
        return jeu