from domino import Domino

class Pioche:
    def __init__(self, dominos):
        self.dominos = dominos

    #verifie si pioche vide (n'arrivera jamais)
    def is_empty(self) -> bool:
        return not self.dominos     
    
    #le nombre de pieces dans la pioche => 28 et 7 quand debute la partie
    def count_pioche(self):
        return len(self.dominos)
    
