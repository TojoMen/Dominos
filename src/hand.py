from src.domino import Domino

class Hand:
    def __init__(self, dominos:list[Domino]):
        self.dominos = dominos
    
    def add(self, domino: Domino):
        self.dominos.append(domino)
    
    
    def remove(self, domino: Domino):
        if domino in self.dominos:
            self.dominos.remove(domino)

    #renvoie la liste des pieces jouables a ce tour
    def playable_tiles(self, end_left, end_right) -> list[Domino]:
        if end_left is None and end_right is None:
            return self.dominos
        return [domino for domino in self.dominos if domino.matches(end_left) or domino.matches(end_right)]
    
    def total(self) -> int:
        total = 0
        for domino in self.dominos:
            total += domino.left_end.value + domino.right_end.value
        return total    