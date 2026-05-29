from domino import Domino

class Hand:
    def __init__(self, dominos):
        self.dominos = dominos
    
    def add(self, domino: Domino):
        self.dominos.append(domino)
    
    
    def remove(self, domino: Domino):
        if domino in self.dominos:
            self.dominos.remove(domino)

    #renvoie la liste des pieces jouables a ce tour
    def playable_tiles(self, end_left, end_right) -> list:
        return [domino for domino in self.dominos if domino.matches(end_left) or domino.matches(end_right)]
    