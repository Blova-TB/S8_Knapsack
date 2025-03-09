import random
from SadObject import Sad
from Solver import Solver
from collections import deque

DEFAULT_TABU_SIZE = 20
DEFAULT_THRESHOLD = 1.1

#ajout item n : 2n+1
#suppresssion item n : 2n

def get_voisin(solution:list,operation) :
    sol = solution.copy()
    sol[int(operation/2)] += (operation & 1) * 2 - 1
    return sol

class Tabou_solver2(Solver) :  
    # liste tabu : liste des transformations interdites
    # Une opération c'est l'ajout ou la suppression d'un élément
    # comment la représenter : entier i = indice de l'élément ajouté ou supprimer
    tabu_list:deque

    #solution courante
    solution = []
    fitness = 0
    poids = 0
    def __init__(self, sad: Sad, iter_max=-1, tabu_size=-1, max_weight:float=-1) : 
        super().__init__(sad, iter_max)
        
        if(tabu_size == -1) :
            self.NB_TABU = getattr(self,"NB_TABU",DEFAULT_TABU_SIZE)
        else :
            self.NB_TABU = tabu_size
        #pas de taille max pour retirer l'élément du set
        self.tabu_list = deque()
        self.tabu_set = set()
        
        if(max_weight == -1) :
            self.THRESHOLD = getattr(self,"THRESHOLD",DEFAULT_THRESHOLD)
        else :
            self.THRESHOLD = max_weight
        
        (self.solution, self.fitness, self.poids) = self.create_rand_solution()
        self.update_sad()
        
    def create_rand_solution(self) :
        randSolut = [0]*self.sad.nbItem
        poids = 0
        fitness = 0
        while (poids < self.sad.capacity * 0.6) :
            i = random.randint(0,self.sad.nbItem-1)
            randSolut[i] += 1
            item = self.sad.listItems[i]
            poids += item.weight
            fitness += item.profit
        return randSolut, fitness, poids
    
    #ne pas appeler si opération négative sur 0 (pas pris en compte)
    def delta_fitness_poids(self,op):
        item = self.sad.listItems[int(op/2)]
        
        if (op & 1) :#si op = 2n +1, donc add
            return item.weight,item.profit
        else :
            return -item.weight,-item.profit

    def get_best_voisin(self, solution) : 
        best_fit = -1
        op=-1
        (fit_base,poids_base) = self.sad.calc_fitness_poids(solution)
        for i in range(0,self.sad.nbItem*2) :
            if not ((i & 1) or solution[int(i/2)] ) :
                #si on fait une soustraction sur 0, on skip.
                #ñi addition
                #ni solution[n] == 0
                continue
            if (i in self.tabu_set) :
                continue
            (d_fitness, d_poids) = self.delta_fitness_poids(i)  
            if (poids_base + d_poids > self.sad.capacity * self.THRESHOLD) :
                continue
            n_fit = fit_base + d_fitness
            if (n_fit >= best_fit) :
                op=i
                best_fit=n_fit
        return op
            
    
    def solve(self) :
        for i in range(0, self.MAX_ITER) :
            op = self.get_best_voisin(self.solution)
            
            if (op == -1) :
                print("block",i)
                #l'algo est bloqué
                break
            voisin = get_voisin(self.solution,op)
            voisin_fit = self.sad.calc_fitness(voisin)
            delta = voisin_fit - self.fitness
            self.update_self_wfitness(voisin,voisin_fit)#on met la solution courrante à jour
            
            if (delta <= 0) and ((op + 1) not in self.tabu_set):
                self.tabu_list.append(op + 1)
                self.tabu_set.add(op + 1)
                # Si la liste dépasse la taille max, retirer l'ancien élément du set aussi
                if len(self.tabu_list) == self.NB_TABU:
                    removed = self.tabu_list.popleft()
                    self.tabu_set.remove(removed)
                    
            if (self.sad.bestFitness <= self.fitness) :
                self.update_sad()#ne le met à jour que si le poids est correct
    
def reinit_tabu_list(self : Tabou_solver2,tabu_size : int) :
    self.sad.reinit()
    return Tabou_solver2(self.sad,self.MAX_ITER,tabu_size,self.THRESHOLD)

def reinit_iter_changer(self : Tabou_solver2,max_iter_number : int) :
    self.sad.reinit()
    return Tabou_solver2(self.sad,max_iter_number,self.NB_TABU,self.THRESHOLD)

def reinit_max_weight(self : Tabou_solver2,percentage_weight_overflow : float) :
    self.sad.reinit()
    return Tabou_solver2(self.sad,self.MAX_ITER,self.NB_TABU,percentage_weight_overflow)    
