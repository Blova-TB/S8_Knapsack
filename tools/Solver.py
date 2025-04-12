import random
from tools.SadObject import Sad
import numpy as np

class Solver :
    sad : Sad
    seed : int
    
    def __init__(self, sad : Sad, seed : int = 0):
        sad.reinit()
        self.sad = sad
        self.seed = seed
        random.seed(self.seed)
        self.item_weights = np.array([sad.get_item(i).weight for i in range(sad.nbItem)])
        self.item_fitnesses = np.array([sad.get_item(i).profit for i in range(sad.nbItem)])

        self.sad_capacity = sad.capacity
        self.sad_nbItem = sad.nbItem


    def solve(self):
        return 0
    
    def calc_short_solut_fit_poids(self,solution:list) :
        fit = 0
        poids = 0
        for i in range(self.sad_nbItem) :
            if solution[i] != 0 :
                fit += self.item_fitnesses[i]
                poids += self.item_weights[i]
        return fit, poids
            