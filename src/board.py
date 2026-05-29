from domino import Domino
class Board:
    def __init__(self, left_end: Pip, right_end: Pip):
        self.left_end = left_end
        self.right_end = right_end
        self.left_dom = list[Domino] = [] 
        self.right_dom = list[Domino] = []

    def place(self, domino: Domino, side):
        if len(self.left_dom) == 0 and len(self.right_dom) == 0 :
            self.left_dom.append(domino)
            self.left_end = domino.left_end
            self.right_end = domino.right_end
            return
        if side == "R" and domino.matches(self.right_end):
            self.right_dom.append(domino)
            self.right_end = domino.right_end
        elif side == "L" and domino.matches(self.left_end):
            self.left_dom.append(domino)
            self.left_end = domino.left_end