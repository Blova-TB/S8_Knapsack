import random
from tools.SadObject import Sad

class Solver :
    sad : Sad
    seed : int
    
    def __init__(self, sad : Sad, seed : int = 0):
        sad.reinit()
        self.sad = sad
        self.seed = seed
        random.seed(self.seed)
        self.item_weights = tuple(sad.get_item(i).weight for i in range(sad.nbItem))
        self.item_fitnesses = tuple(sad.get_item(i).profit for i in range(sad.nbItem))     

    def solve(self):
        return 0
    
            