import random
from SadObject import Sad
from Solver import Solver
from collections import deque

DEFAULT_TABU_SIZE = 30
DEFAULT_THRESHOLD = 1
DEFAULT_MAX_ITER = 200
DEFAULT_SOLUTION_SIZE = 0.5

def get_voisin(solution:list,operation:int) :
    sol = solution.copy()
    sol[operation] = not sol[operation]
    return sol

class Tabou_solver(Solver) :
    # liste tabu : liste des transformations interdites
    # Une opération c'est l'ajout ou la suppression d'un élément
    # comment la représenter : entier i = indice de l'élément ajouté ou supprimer
    tabu_list: deque

    #solution courante
    solution:list[bool]
    fitness:int
    poids:int
    

    def __init__(self, sad: Sad, iter_max=-1, tabu_size=-1, max_weight:float=-1, def_sol_size:float=-1) :
        sad.reinit()
        self.sad = sad
        if(iter_max == -1) :
             self.MAX_ITER = getattr(self, "MAX_ITER", DEFAULT_MAX_ITER)
        else :
            self.MAX_ITER = iter_max
            
        if(def_sol_size == -1) :
            self.DEF_SOL_SIZE = getattr(self,"DEF_SOL_SIZE",DEFAULT_SOLUTION_SIZE)
        else :
            self.DEF_SOL_SIZE = def_sol_size
        
        if(tabu_size == -1) :
            self.NB_TABU = getattr(self,"NB_TABU",DEFAULT_TABU_SIZE)
        else :
            self.NB_TABU = tabu_size
        
        self.tabu_list = deque()
        self.tabu_set = set()
        
        if(max_weight == -1) :
            self.THRESHOLD = getattr(self,"THRESHOLD",DEFAULT_THRESHOLD)
        else :
            self.THRESHOLD = max_weight
        
        self.create_rand_solution()
        self.update_sad()
    
    def update_self_wfitness(self, solution, fitness) :
        self.solution = solution
        self.fitness = fitness
        self.poids = self.sad.calc_poids(self.solution)
    
    def update_self(self,solution) :
        self.update_self_wfitness(solution,self.sad.calc_fitness(solution))

    def update_sad(self) :
        if (self.poids <= self.sad.capacity) :
            self.sad.bestSolution = self.solution.copy()
            self.sad.bestFitness = self.fitness

    
    def create_rand_solution(self) :
        self.solution = [False]*self.sad.nbItem
        self.fitness = 0
        self.poids = 0
        while (self.poids < self.sad.capacity * self.DEF_SOL_SIZE) :
            i = random.randint(0,self.sad.nbItem-1)
            if (not self.solution[i]) :
                self.solution[i] = True
                item = self.sad.get_item(i)
                self.poids += item.weight
                self.fitness += item.profit
    
    def delta_fitness_poids_voisin(self,solution,op):
        item = self.sad.get_item(op)
        if (solution[op]) :
            return -item.weight,-item.profit
        else :
            return item.weight,item.profit

    def get_best_voisin(self) :
        best_fitness = -1000
        op=-1
        for i in range(0,self.sad.nbItem) :
            if (i in self.tabu_set) :
                continue
            
            item = self.sad.get_item(i)
            if(self.solution[i]) :
                new_fitness= self.fitness - item.profit
                if (new_fitness >= best_fitness) :
                    best_fitness = new_fitness
                    op=i
            elif (self.poids + item.weight <= self.sad.capacity * self.THRESHOLD) :
                new_fitness= self.fitness + item.profit
                if (new_fitness > best_fitness) :
                    best_fitness = new_fitness
                    op=i
                
        return best_fitness, op
            
    
    def solve(self) :
        for _ in range(0, self.MAX_ITER) :
            (voisin_fitness,op) = self.get_best_voisin()
            if (op == -1) :
                #l'algo est bloqué
                break
            delta = voisin_fitness - self.fitness
            self.update_self_wfitness(get_voisin(self.solution,op),voisin_fitness)#on met la solution courrante à jour
            self.poids = self.sad.calc_poids(self.solution)
            
            if (delta < 0) :
                #si c'est moins bien, on met dans la liste tabu
                self.tabu_list.append(op)
                self.tabu_set.add(op)
                if (len(self.tabu_list) > self.NB_TABU) :
                    supp = self.tabu_list.popleft()
                    self.tabu_set.remove(supp)

            if (self.sad.bestFitness <= self.fitness) :
                self.update_sad()#ne le met à jour que si le poids est correct
    
def reinit_tabu_list(self : Tabou_solver,tabu_size : int) :
    return Tabou_solver(self.sad,self.MAX_ITER,tabu_size,self.THRESHOLD,self.DEF_SOL_SIZE)

def reinit_iter_changer(self : Tabou_solver,max_iter_number : int) :
    return Tabou_solver(self.sad,max_iter_number,self.NB_TABU,self.THRESHOLD,self.DEF_SOL_SIZE)

def reinit_max_weight(self : Tabou_solver,percentage_weight_overflow : float) :
    return Tabou_solver(self.sad,self.MAX_ITER,self.NB_TABU,percentage_weight_overflow,self.DEF_SOL_SIZE)

def reinit_solution_size(self : Tabou_solver,default_solution_size : float) :
    return Tabou_solver(self.sad,self.MAX_ITER,self.NB_TABU,self.THRESHOLD,default_solution_size)
