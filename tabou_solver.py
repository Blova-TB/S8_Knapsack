import random
from SadObject import Sad
from Solver import Solver

DEFAULT_TABU_SIZE = 20

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
            if (not self.tabu_size) :
                self.NB_TABU = DEFAULT_TABU_SIZE
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

    def get_voisin(self,solution,operation) :
        if (len(solution) != self.sad.nbItem) :
            print(solution)
            assert(False)
        assert(operation < len(solution))
        sol = solution.copy()
        sol[operation] = 1 - sol[operation]
        return sol
    
    def get_best_voisin(self, solution) : 
        best_voisin = []
        best_fitness = -1
        op=-1
        for i in range(0,self.sad.nbItem) :
            if (i in self.tabu_list) :
                continue
            voisin = self.get_voisin(solution,i)
            fitness = self.sad.calc_fitness(voisin)
            poids = self.sad.calc_poids(voisin)

            if (fitness >= best_fitness and poids <= self.sad.capacity * 1.2) :
                best_fitness = fitness
                best_voisin = voisin
                op = i
                
        return best_voisin, best_fitness, op 
            
    
    def solve(self) : 
        #init boucle
        for i in range(0, self.MAX_ITER) :
            (best_voisin, voisin_fitness,op) = self.get_best_voisin(self.solution)
            if (op == -1) :
                #l'algo est bloqué
                return
            delta = voisin_fitness - self.fitness
            #print(i,":",len(best_voisin),"/",self.sad.nbItem, " with a value of",voisin_fitness, " with the op ",op)
            self.update_self(best_voisin,voisin_fitness)#on met la solution courrante à jour
            
            if (delta <= 0) :
                #si c'est moins bien, on met dans la liste tabu
                self.tabu_list.append(op)
                if (len(self.tabu_list) > self.NB_TABU) :
                    self.tabu_list.pop(0)
            if (self.sad.bestFitness <= self.fitness and self.poids <= self.sad.capacity) :
                self.update_sad()

    def update_self(self, solution ,fitness) :
        self.solution = solution.copy()
        self.fitness = fitness
        self.poids = self.sad.calc_poids(self.solution)
    
def reinit_tabu_list(self : Tabou_solver,tabu_size : int) :
    self.sad.reinit()
    return Tabou_solver(self.sad,tabu_size,self.MAX_ITER)

def reinit_iter_changer(self : Tabou_solver,max_iter_number : int) :
    self.sad.reinit()
    return Tabou_solver(self.sad,self.NB_TABU,max_iter_number)    
