from domino import Domino

class Pioche:
    def __init__(self, dominos):
        self.dominos = dominos

    def is_empty(self) -> bool:
        return not self.dominos     
    
    def count_pioche(self):
        return len(self.dominos)
    
