from SadObject import Sad

DEFAULT_MAX_ITER = 20

class Solver :
    def __init__(self, sad : Sad, iter_max=-1, *args) :
        sad.reinit()
        self.sad = sad            
        if(iter_max == -1) :
             self.MAX_ITER = getattr(self, "MAX_ITER", DEFAULT_MAX_ITER)
        else :
            self.MAX_ITER = iter_max
    
    def update_self_wfitness(self, solution, fitness) :
        self.solution = solution
        self.fitness = fitness
        self.poids = self.sad.calc_poids(self.solution)
    
    def update_self(self,solution) :
        self.update_self(solution,self.sad.calc_fitness(solution))

    def update_sad(self) : 
        if (self.poids <= self.sad.capacity) :
            self.sad.bestSolution = self.solution.copy()
            self.sad.bestFitness = self.fitness

    def solve(self):
        return
    
            