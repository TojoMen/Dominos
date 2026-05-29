from pip_enum import Pip

class Domino:
    def __init__(self, left_end: Pip, right_end: Pip):
        self.left_end = left_end
        self.right_end = right_end
    
    #Verifie Double
    def is_double(self) -> bool:
       return self.left_end == self.right_end
    
    #Verifie validité du domino
    def matches(self, end:Pip) -> bool:
        return self.left_end == end or self.right_end == end
    
    