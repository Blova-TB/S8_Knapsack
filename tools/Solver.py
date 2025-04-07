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
        return

    def solve(self):
        return
    
            