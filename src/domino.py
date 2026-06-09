from pip_enum import Pip
from side import Side
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
    
    def choix_coté(self, left:Pip, right:Pip):
        if self.left_end == left and self.left_end == right:
            return True
        if self.right_end == left and self.right_end == right:
            return True
        if self.left_end == left and self.right_end == right:
            return True
        if self.right_end == left and self.left_end == right:
            return True
        return False
    
    def is_a_inverser(self, end:Pip, side:Side) -> bool:
        if self.left_end == end and side == Side.LEFT or self.right_end == end and side == Side.RIGHT:
            return True
        return False
        
    def inverser(self):
        left = self.left_end
        right = self.right_end

        self.right_end = left
        self.left_end =  right

    def to_string(self)-> str:
        return "[" + str(self.left_end.value) + "|" + str(self.right_end.value) + "]"