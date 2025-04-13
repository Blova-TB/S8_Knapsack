import random
from tools.SadObject import Sad
from tools.Solver import Solver
from collections import deque
import numpy as np
import pyopencl as cl

DEFAULT_TABU_SIZE = 30
DEFAULT_THRESHOLD = 1
DEFAULT_MAX_ITER = 200
DEFAULT_SOLUTION_SIZE = 0.5


class openCLcompute :
    def __init__(self,ctx=None,queue=None,cprog=None):
        self.create_context(ctx)
        self.create_queue(queue)
        self.mf = cl.mem_flags
        
        if cprog==None :
            self.compile_prog()
        else : self.localcalc = cprog

    def init_glob_var(self,item_weights,item_fitnesses,capacity,neg_overflow,solution_like) :
        self.weights_buf = cl.Buffer(self.ctx, self.mf.READ_ONLY | self.mf.COPY_HOST_PTR, hostbuf=item_weights)
        self.fitnesses_buf = cl.Buffer(self.ctx, self.mf.READ_ONLY | self.mf.COPY_HOST_PTR, hostbuf=item_fitnesses)
        self.solution_buf = cl.Buffer(self.ctx, self.mf.READ_ONLY, size=solution_like.nbytes)
        self.tabu_buf = self.tabu_buf = cl.Buffer(self.ctx, self.mf.READ_ONLY, size=solution_like.nbytes)
        
        self.temp_rslt = np.empty_like(item_weights,dtype=np.float32)
        self.temp_buf = cl.Buffer(self.ctx, self.mf.WRITE_ONLY | self.mf.COPY_HOST_PTR, hostbuf=self.temp_rslt)
        
        self.nover = np.float32(neg_overflow)
        self.capa = np.int32(capacity)
        self.nbitem = len(item_fitnesses)

    
    def compute(self,solution,poids,tabu_list) :
        cl.enqueue_copy(self.queue, self.solution_buf, solution)
        cl.enqueue_copy(self.queue, self.tabu_buf, tabu_list)
        
        self.localcalc.compute_temp(
            self.queue, (self.nbitem,), None,
            self.solution_buf, self.weights_buf, self.fitnesses_buf, self.tabu_buf,
            np.int32(poids), self.capa, self.nover,
            self.temp_buf
        )
        cl.enqueue_copy(self.queue, self.temp_rslt, self.temp_buf)
            
        best_id = np.argmax(self.temp_rslt)
        return (0,-1) if (self.temp_rslt[best_id] == np.float32(-1048576.0)) else (self.temp_rslt[best_id],best_id)

    def create_context(self,ctx=None) :
        if ctx == None : 
            self.ctx = cl.create_some_context(False)
            i = 0
            
            for gpu in self.ctx.get_info(cl.context_info.DEVICES): 
                i+=1
                print("mem of gpu ",i,":",gpu.global_mem_size)
                print("max group size",i,":",gpu.max_work_group_size)
        else : self.ctx = ctx
        
        self.maxgroupsize = np.iinfo(np.int16).min
        print(self.maxgroupsize)
        for gpu in self.ctx.get_info(cl.context_info.DEVICES): 
            if gpu.max_work_group_size < self.maxgroupsize :
                self.maxgroupsize = gpu.max_work_group_size

    def create_queue(self,queue=None) :
        if queue == None :
            self.queue = cl.CommandQueue(self.ctx)
        else : self.queue = queue
    
    def compile_prog(self) :
        compute_local_temp = """
                    __kernel void compute_temp(
                        __global const char *solution,
                        __global const int *item_weights,
                        __global const int *item_fitnesses,
                        __global const char *tabu_list,
                        const int poids,
                        const int capacity,
                        const float overflow_cost,  // overflow_cost reste en float pour la précision
                        __global float *temp_out)
                    {
                        int i = get_global_id(0);
                        
                        // Calcul de flip
                        int flip = 1 - 2 * solution[i];
                        // Calcul du poids après "flip" en entier
                        int flipped_weights = flip * item_weights[i] + poids;

                        // Calcul initial de temp 
                        float temp = flip * item_fitnesses[i];

                        // Gestion de l'overflow
                        if (flipped_weights > capacity) {
                            temp -= (flipped_weights - capacity) * overflow_cost;
                        }

                        // Application de la condition tabu
                        if (tabu_list[i]) {
                            temp = -1048576.f;  // Utilisation d'une valeur minimale pour neutraliser les mouvements tabous
                        }

                        // Affectation du résultat dans temp_out
                        temp_out[i] = temp;

                    }
                    
        """
        self.localcalc = cl.Program(self.ctx, compute_local_temp).build()

def get_voisin(solution:list,operation:int) :
    sol = solution.copy()
    sol[operation] = not sol[operation]
    return sol

class tabou_opencl_solver(Solver) :
    # liste tabu : liste des transformations interdites
    # Une opération c'est l'ajout ou la suppression d'un élément
    # comment la représenter : entier i = indice de l'élément ajouté ou supprimer

    #solution courante
    true_fitness:np.int32 #fitness "réelle du SAD "
    poids:np.int32 
    
    poids_overflow:np.int32   #poids en trop
    raw_fitness:np.int32      #fitness absolue 
    neg_fitness:np.int32      #fitness négative venant du poids en trop
    

    def __init__(self, sad: Sad, iter_max=-1, tabu_size=-1, cout_depassement:float=-1, def_sol_size:float=-1,seed=1) :
        super().__init__(sad,seed)
        
        self.item_weights = np.array(self.item_weights,dtype=np.int32)
        self.item_fitnesses = np.array(self.item_fitnesses,dtype=np.int32)
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
        
        self.tabu_pseudo_list = np.zeros(self.sad.nbItem,dtype=np.int8)
        self.tabu_deque = deque()
        
        if(cout_depassement == -1) :
            self.OVERFLOW_COST = getattr(self,"OVERFLOW_COST",DEFAULT_THRESHOLD)
        else :
            self.OVERFLOW_COST = cout_depassement
        
        
        self.create_rand_solution()
        self.update_sad()
        
        self.oCLpc = openCLcompute()
        self.oCLpc.init_glob_var(self.item_weights,self.item_fitnesses,self.sad.capacity,self.OVERFLOW_COST,self.solution)
    
    def udpate_true_fitness_after_all_raw_set(self) :
        self.poids_overflow = self.poids - self.sad.capacity 
        if (self.poids_overflow > 0) :
            self.true_fitness = self.raw_fitness - self.poids_overflow * self.OVERFLOW_COST
        else :
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
        self.solution = np.zeros(self.sad.nbItem,dtype=np.int8)
        self.poids = 0
        self.raw_fitness = 0
        nbItems = 0
        while (self.poids < self.sad.capacity * self.DEF_SOL_SIZE) :
            i = random.randint(0,self.sad.nbItem-1)
            if (not self.solution[i]) :
                nbItems += 1
                self.solution[i] = 1
                self.poids += self.item_weights[i]
                self.raw_fitness += self.item_fitnesses[i]
                if (nbItems == self.sad.nbItem) :
                    break
        self.udpate_true_fitness_after_all_raw_set()
    
    def get_best_voisin(self) :
        return self.oCLpc.compute(self.solution,self.poids,self.tabu_pseudo_list)
    
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
        iterator = range(0, self.MAX_ITER)
        for _ in  iterator :
            (delta,op) = self.get_best_voisin()
            if (op == -1) :
                #l'algo est bloqué
                break
            
            if (delta <= 0 ) :
                #si c'est moins bien, on met dans la liste tabu
                self.tabu_pseudo_list[op]= 1
                self.tabu_deque.append(op)
                if (len(self.tabu_deque) > self.NB_TABU) :
                    poped = self.tabu_deque.popleft()
                    self.tabu_pseudo_list[poped] = 0
            self.update_self_with_op(op)
            if (self.sad.bestFitness <= self.true_fitness) :
                self.update_sad()
        print(f"opencl {_} iter")
        return self.sad.bestFitness, self.sad.bestSolution
    
def reinit_tabu_list(self : tabou_opencl_solver,tabu_size : int) :
    return tabou_opencl_solver(self.sad,self.MAX_ITER,tabu_size,self.OVERFLOW_COST,self.DEF_SOL_SIZE,self.seed+1)

def reinit_iter_changer(self : tabou_opencl_solver,max_iter_number : int) :
    return tabou_opencl_solver(self.sad,max_iter_number,self.NB_TABU,self.OVERFLOW_COST,self.DEF_SOL_SIZE,self.seed+1)

def reinit_overflow_points(self : tabou_opencl_solver,percentage_weight_overflow : float) :
    return tabou_opencl_solver(self.sad,self.MAX_ITER,self.NB_TABU,percentage_weight_overflow,self.DEF_SOL_SIZE,self.seed+1)

def reinit_solution_size(self : tabou_opencl_solver,default_solution_size : float) :
    return tabou_opencl_solver(self.sad,self.MAX_ITER,self.NB_TABU,self.OVERFLOW_COST,default_solution_size,self.seed+1)

class variateur_tabou2 : 
    def liste_tabou2() :
        return reinit_tabu_list, "fitness en fonction de la taille de la liste TABU"
    def nombre_iterations() :
        return  reinit_iter_changer, "fitness en fonction du nombre d'itérations"
    def compte_negatif_des_points() :
        return reinit_overflow_points, "fitness en fonction du facteur négatif d'overflow"
    def poids_inital() :
        return reinit_solution_size, "fitness fct taille solution initiale"