from SadObject import Sad

DEFAULT_MAX_ITER = 20

class Solver :
    def __init__(self, sad : Sad, iter_max=-1, *args) :
        self.sad = sad            
        if(iter_max == -1) :
             self.MAX_ITER = getattr(self, "MAX_ITER", DEFAULT_MAX_ITER)
        else :
            self.MAX_ITER = iter_max
    
    def solve(self):
        return
    
            