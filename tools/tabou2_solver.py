import random
from tools.SadObject import Sad
from tools.Solver import Solver
from collections import deque

DEFAULT_TABU_SIZE = 30
DEFAULT_THRESHOLD = 1
DEFAULT_MAX_ITER = 200
DEFAULT_SOLUTION_SIZE = 0.5

def get_voisin(solution:list,operation:int) :
    sol = solution.copy()
    sol[operation] = not sol[operation]
    return sol

class tabou2_solver(Solver) :
    # liste tabu : liste des transformations interdites
    # Une opération c'est l'ajout ou la suppression d'un élément
    # comment la représenter : entier i = indice de l'élément ajouté ou supprimer
    tabu_list: deque

    #solution courante
    solution:list[bool]
    true_fitness:int #fitness "réelle du SAD "
    poids:int
    
    poids_overflow:int  #poids en trop
    raw_fitness:int     #fitness absolue 
    neg_fitness:int     #fitness négative venant du poids en trop
    

    def __init__(self, sad: Sad, iter_max=-1, tabu_size=-1, cout_depassement:float=-1, def_sol_size:float=-1) :
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
        
        if(cout_depassement == -1) :
            self.OVERFLOW_COST = getattr(self,"OVERFLOW_COST",DEFAULT_THRESHOLD)
        else :
            self.OVERFLOW_COST = cout_depassement
        
        self.create_rand_solution()
        self.update_sad()
    
    def udpate_true_fitness_after_all_raw_set(self) :
        if (self.poids > self.sad.capacity) :
            self.poids_overflow = self.poids - self.sad.capacity
            self.true_fitness = self.raw_fitness - self.poids_overflow * self.OVERFLOW_COST
        else :
            self.poids_overflow = 0
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
    
    def create_rand_solution(self) :
        self.solution = [False]*self.sad.nbItem
        self.raw_fitness = 0
        self.poids = 0
        nbItems = 0
        while (self.poids < self.sad.capacity * self.DEF_SOL_SIZE) :
            i = random.randint(0,self.sad.nbItem-1)
            if (not self.solution[i]) :
                nbItems += 1
                self.solution[i] = True
                item = self.sad.get_item(i)
                self.poids += item.weight
                self.raw_fitness += item.profit
            elif (nbItems == self.sad.nbItem) :
                break
        self.udpate_true_fitness_after_all_raw_set()
    
    def true_fitness_voisin(self,op):
        item = self.sad.get_item(op)
        if (self.solution[op]) : #on la retire
            if (self.poids_overflow > 0 ) :#on est déjà au delà de la capa
                #ici on utilise seulement la fitness égale à la somme de la fitness des objets
                return self.raw_fitness - item.profit - self.calc_neg_points_of_weight(self.poids - item.weight) 
            else : #si on est en dessous, juste a retirer le profit
                return self.true_fitness - item.profit
        else : #on l'ajoute
            return self.raw_fitness + item.profit - self.calc_neg_points_of_weight(self.poids + item.weight)
    
    def get_best_voisin(self) :
        best_fit = -10000
        op=-1
        for i in range(0,self.sad.nbItem) :
            if (i in self.tabu_set) :
                continue
            
            new_fit = self.true_fitness_voisin(i)
            if (new_fit > best_fit) :
                best_fit = new_fit
                op=i
        return best_fit, op
    
    def update_self_with_op(self,op,true_fit) :
        item = self.sad.get_item(op)
        
        if(self.solution[op]) :#existe déjà
            self.poids -= item.weight
            self.raw_fitness -= item.profit
        else :
            self.poids += item.weight
            self.raw_fitness += item.profit
        
        self.poids_overflow = self.poids - self.sad.capacity
        if self.poids_overflow < 0 :
            self.poids_overflow = 0
        self.true_fitness = true_fit
        self.solution = get_voisin(self.solution,op)
    
    def solve(self) :
        for _ in range(0, self.MAX_ITER) :
            (voisin_fit,op) = self.get_best_voisin()
            if (op == -1) :
                #l'algo est bloqué
                break
            
            if (voisin_fit <= self.true_fitness ) :
                #si c'est moins bien, on met dans la liste tabu
                self.tabu_list.append(op)
                self.tabu_set.add(op)
                if (len(self.tabu_list) > self.NB_TABU) :
                    supp = self.tabu_list.popleft()
                    self.tabu_set.remove(supp)
            
            self.update_self_with_op(op,voisin_fit)        
            
            if (self.sad.bestFitness <= self.true_fitness) :
                self.update_sad()
        return self.sad.bestFitness, self.sad.bestSolution
    
def reinit_tabu_list(self : tabou2_solver,tabu_size : int) :
    return tabou2_solver(self.sad,self.MAX_ITER,tabu_size,self.OVERFLOW_COST,self.DEF_SOL_SIZE)

def reinit_iter_changer(self : tabou2_solver,max_iter_number : int) :
    return tabou2_solver(self.sad,max_iter_number,self.NB_TABU,self.OVERFLOW_COST,self.DEF_SOL_SIZE)

def reinit_overflow_points(self : tabou2_solver,percentage_weight_overflow : float) :
    return tabou2_solver(self.sad,self.MAX_ITER,self.NB_TABU,percentage_weight_overflow,self.DEF_SOL_SIZE)

def reinit_solution_size(self : tabou2_solver,default_solution_size : float) :
    return tabou2_solver(self.sad,self.MAX_ITER,self.NB_TABU,self.OVERFLOW_COST,default_solution_size)

class variateur_tabou2 : 
    def liste_tabou2() :
        return reinit_tabu_list, "fitness en fonction de la taille de la liste TABU"
    def nombre_iterations() :
        return  reinit_iter_changer, "fitness en fonction du nombre d'itérations"
    def compte_negatif_des_points() :
        return reinit_overflow_points, "fitness en fonction du facteur négatif d'overflow"
    def poids_inital() :
        return reinit_solution_size, "fitness fct taille solution initiale"