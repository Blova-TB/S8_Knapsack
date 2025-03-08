import random
from SadObject import Sad
from Solver import Solver

DEFAULT_TABU_SIZE = 20

def get_voisin(solution,operation) :
    sol = solution.copy()
    sol[operation] = 1 - sol[operation]
    return sol

class Tabou_solver(Solver) :  
    #taille max de la liste tabou
    # liste tabu : liste des transformations interdites
    # Une opération c'est l'ajout ou la suppression d'un élément
    # comment la représenter : entier i = indice de l'élément ajouté ou supprimer
    tabu_list = []

    #solution courante
    solution = []
    fitness = 0
    poids = 0

    def __init__(self, sad: Sad, iter_max=-1, tabu_size=-1) : 
        super().__init__(sad, iter_max)
        
        if(tabu_size == -1) :
            self.NB_TABU = getattr(self,"NB_TABU",DEFAULT_TABU_SIZE)
        else :
            self.NB_TABU = tabu_size
        
        (self.solution, self.fitness, self.poids) = self.create_rand_solution()
        self.update_sad()

    def update_sad(self) : 
        if (self.poids <= self.sad.capacity) :
            self.sad.bestSolution = self.solution.copy()
            self.sad.bestFitness = self.fitness
        
    def create_rand_solution(self) :
        randSolut = [0]*self.sad.nbItem
        poids = 0
        fitness = 0
        while (poids < self.sad.capacity * 0.6) :
            i = random.randint(0,self.sad.nbItem-1)
            if (randSolut[i] == 0 ) :
                randSolut[i] = 1
                item = self.sad.listItems[i]
                poids += item.weight
                fitness += item.profit
        return randSolut, fitness, poids
    
    def delta_fitness_poids_voisin(self,solution,op):
        item = self.sad.listItems[op]
        if (solution[op]) :
            return (-item.weight,-item.profit)
        else :
            return (item.weight,item.profit) 

    def get_best_voisin(self, solution) : 
        best_fitness = -1
        op=-1
        (fitness_base, poids_base) = self.sad.calc_fitness_poids(solution)
        for i in range(0,self.sad.nbItem) :
            if (i in self.tabu_list) :
                continue
            (d_fitness, d_poids) = self.delta_fitness_poids_voisin(solution,i)
            n_fitness = fitness_base + d_fitness 
            n_poids = poids_base + d_poids 
            
            if (n_fitness > best_fitness and n_poids < self.sad.capacity * 1.2) :
                best_fitness = n_fitness
                op=i
                
        return best_fitness, op
            
    
    def solve(self) : 
        for i in range(0, self.MAX_ITER) :
            (voisin_fitness,op) = self.get_best_voisin(self.solution)
            if (op == -1) :
                #l'algo est bloqué
                break
            delta = voisin_fitness - self.fitness
            self.update_self(get_voisin(self.solution,op),voisin_fitness)#on met la solution courrante à jour
            
            if (delta <= 0) :
                #si c'est moins bien, on met dans la liste tabu
                self.tabu_list.append(op)
                if (len(self.tabu_list) > self.NB_TABU) :
                    self.tabu_list.pop(0)
            if (self.sad.bestFitness <= self.fitness and self.poids <= self.sad.capacity) :
                self.update_sad()

    def update_self(self, solution ,fitness) :
        self.solution = solution
        self.fitness = fitness
        self.poids = self.sad.calc_poids(self.solution)
    
def reinit_tabu_list(self : Tabou_solver,tabu_size : int) :
    self.sad.reinit()
    return Tabou_solver(self.sad,tabu_size=tabu_size,iter_max=self.MAX_ITER)

def reinit_iter_changer(self : Tabou_solver,max_iter_number : int) :
    self.sad.reinit()
    return Tabou_solver(self.sad,tabu_size=self.NB_TABU,iter_max=max_iter_number)    
