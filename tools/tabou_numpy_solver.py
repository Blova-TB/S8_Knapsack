import random
from tools.SadObject import Sad
from tools.Solver import Solver
from collections import deque
import numpy as np
DEFAULT_TABU_SIZE = 30
DEFAULT_THRESHOLD = 1
DEFAULT_MAX_ITER = 200
DEFAULT_SOLUTION_SIZE = 0.5

def get_voisin(solution:list,operation:int) :
    sol = solution.copy()
    sol[operation] = not sol[operation]
    return sol

class tabou_numpy_solver(Solver) :
    # liste tabu : liste des transformations interdites
    # Une opération c'est l'ajout ou la suppression d'un élément
    # comment la représenter : entier i = indice de l'élément ajouté ou supprimer
    tabu_list: deque

    #solution courante 
    #numpy array booléen
    true_fitness:int #fitness "réelle du SAD "
    poids:int
    
    poids_overflow:int  #poids en trop
    raw_fitness:int     #fitness absolue 
    neg_fitness:int     #fitness négative venant du poids en trop
    

    def __init__(self, sad: Sad, iter_max=-1, tabu_size=-1, cout_depassement:float=-1, def_sol_size:float=-1,seed=1) :
        super().__init__(sad,seed)
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
        
        if(cout_depassement == -1) :
            self.OVERFLOW_COST = getattr(self,"OVERFLOW_COST",DEFAULT_THRESHOLD)
        else :
            self.OVERFLOW_COST = cout_depassement
        
        self.create_rand_solution()
        self.update_sad()
    
    def udpate_true_fitness_after_all_raw_set(self) :
        self.poids_overflow = self.poids - self.sad.capacity 
        if (self.poids_overflow > 0) :
            self.neg_fitness = self.poids_overflow * self.OVERFLOW_COST
            self.true_fitness = self.raw_fitness - self.neg_fitness
        else :
            self.neg_fitness = 0
            self.true_fitness = self.raw_fitness
    
    def update_self_wfitness_n_weight(self,solution, fitness,weight) :
        self.solution = solution
        self.raw_fitness = fitness
        self.poids = weight
        self.udpate_true_fitness_after_all_raw_set()
            
    def update_sad(self) :
        if self.poids <= self.sad.capacity :
            self.sad.bestSolution = self.solution.copy()
            self.sad.bestFitness = self.true_fitness
    
    #pour calculer true_fitness = raw_fitness - resultat
    def calc_neg_points_of_weight(self,poids) :
        diff = poids - self.sad.capacity
        return diff * self.OVERFLOW_COST if (diff > 0) else 0
    
    def calc_neg_point_of_weight_diff(self,diff) :
        return diff * self.OVERFLOW_COST if (diff > 0) else 0
    
    def create_rand_solution(self) :
        self.solution = np.zeros(self.sad.nbItem,dtype=bool)
        self.raw_fitness = 0
        self.poids = 0
        nbItems = 0
        while (self.poids < self.sad.capacity * self.DEF_SOL_SIZE) :
            i = random.randint(0,self.sad.nbItem-1)
            if (not self.solution[i]) :
                nbItems += 1
                self.solution[i] = True
                self.poids += self.item_weights[i]
                self.raw_fitness += self.item_fitnesses[i]
            elif (nbItems == self.sad.nbItem) :
                break
        self.udpate_true_fitness_after_all_raw_set()
    
    def delta_fitness_voisin(self,op):
        f = self.item_fitnesses[op]
        w = self.item_weights[op]
        if (self.solution[op]) : #on la retire

            if (self.poids_overflow > w ) :
                #poids > capa + weight ; donc on il y a toujours une diff
                return - f + self.calc_neg_point_of_weight_diff(w) 
            #si poids <= capa + weight, juste a retirer (le profit + la fitness négative)
            #si on est déjà en dessous, neg fitness = 0 donc ça marche
            return self.neg_fitness - f
        #on l'ajoute]
        if (self.poids_overflow >= 0) :
            return f - self.calc_neg_point_of_weight_diff(w)
        elif ( - self.poids_overflow >= w) :#si l'item rentre
            return f
        #si item.weight > marge restante
        return f - self.calc_neg_point_of_weight_diff(w + self.poids_overflow)
            
    def get_meilleur_op(self):
        flip = (1 - self.solution * 2)
        flipped_weights = flip * self.item_weights + self.poids
        
        temp = flip * self.item_fitnesses 
        overflow = flipped_weights > self.sad.capacity
        temp[overflow] -= ((flipped_weights[overflow] - self.sad.capacity) * self.OVERFLOW_COST).astype(int)

        min = np.iinfo(np.int32).min
        # On neutralise les mouvements tabous
        temp[list(self.tabu_list)] = min
        # On récupère le meilleur mouvement
        best_id = np.argmax(temp)
        return best_id if temp[best_id] > min else -1

    def get_best_voisin(self) :
        op = self.get_meilleur_op()
        if (op == -1) :
            return 0,-1
        else :
            return self.delta_fitness_voisin(op), op
    
    def update_self_with_op(self,op) :
        if(self.solution[op]) :#existe déjà
            self.poids -= self.item_weights[op]
            self.raw_fitness -= self.item_fitnesses[op]
        else :
            self.poids += self.item_weights[op]
            self.raw_fitness += self.item_fitnesses[op]
        
        self.udpate_true_fitness_after_all_raw_set()
        self.solution = get_voisin(self.solution,op)
    
    def solve(self) :
        for _ in range(0, self.MAX_ITER) :
            (delta,op) = self.get_best_voisin()
            if (op == -1) :
                #l'algo est bloqué
                break
            if (delta <= 0 ) :
                #si c'est moins bien, on met dans la liste tabu
                self.tabu_list.append(op)
                if (len(self.tabu_list) > self.NB_TABU) :
                    self.tabu_list.popleft()
            
            self.update_self_with_op(op)
            if (self.sad.bestFitness <= self.true_fitness) :
                self.update_sad()
        return self.sad.bestFitness, self.sad.bestSolution
    
def reinit_tabu_list(self : tabou_numpy_solver,tabu_size : int) :
    return tabou_numpy_solver(self.sad,self.MAX_ITER,tabu_size,self.OVERFLOW_COST,self.DEF_SOL_SIZE,self.seed+1)

def reinit_iter_changer(self : tabou_numpy_solver,max_iter_number : int) :
    return tabou_numpy_solver(self.sad,max_iter_number,self.NB_TABU,self.OVERFLOW_COST,self.DEF_SOL_SIZE,self.seed+1)

def reinit_overflow_points(self : tabou_numpy_solver,percentage_weight_overflow : float) :
    return tabou_numpy_solver(self.sad,self.MAX_ITER,self.NB_TABU,percentage_weight_overflow,self.DEF_SOL_SIZE,self.seed+1)

def reinit_solution_size(self : tabou_numpy_solver,default_solution_size : float) :
    return tabou_numpy_solver(self.sad,self.MAX_ITER,self.NB_TABU,self.OVERFLOW_COST,default_solution_size,self.seed+1)

class variateur_tabou_numpy : 
    def liste_tabou2() :
        return reinit_tabu_list, "fitness en fonction de la taille de la liste TABU"
    def nombre_iterations() :
        return  reinit_iter_changer, "fitness en fonction du nombre d'itérations"
    def compte_negatif_des_points() :
        return reinit_overflow_points, "fitness en fonction du facteur négatif d'overflow"
    def poids_inital() :
        return reinit_solution_size, "fitness fct taille solution initiale"