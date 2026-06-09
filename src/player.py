from hand import Hand

class Player:
    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.hand = Hand([])
        self.score = 0
        
    
        