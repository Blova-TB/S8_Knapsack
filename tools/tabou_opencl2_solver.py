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

def next_power_of_two(x):
    return 1 << (x - 1).bit_length()

class openCLcompute :
    def __init__(self,ctx=None,queue=None,nbitem=None):
        self.create_context(ctx)#créé le contexte
        self.create_queue(queue)#la queue de commande
        self.mf = cl.mem_flags
        self.adaptkernelsizes(nbitem) # calcul la taille des groupes pour la réduction

        self.compile_progs()#compile les programe avec la taille des groupes

        
    def adaptkernelsizes(self,nbitem) :
        remainder = nbitem % self.local_size
        if remainder != 0:
            self.global_size = nbitem + (self.local_size - remainder)
        else:
           self.global_size = nbitem
           
        self.nb_groups = self.global_size // self.local_size
           
    def create_context(self,ctx=None) :
        if ctx == None : 
            self.ctx = cl.create_some_context(False)
            i = 0
            
            for gpu in self.ctx.get_info(cl.context_info.DEVICES): 
                i+=1
                print("mem of gpu ",i,":",gpu.global_mem_size)
                print("max group size",i,":",gpu.max_work_group_size)
        else : self.ctx = ctx
        
        maxgroupsize = np.iinfo(np.int16).max
        for gpu in self.ctx.get_info(cl.context_info.DEVICES): 
            if gpu.max_work_group_size < maxgroupsize :
                maxgroupsize = gpu.max_work_group_size
        self.local_size = min(256,maxgroupsize)
        if (self.local_size != 256 ) : raise ValueError("PAS GROSSE CARTE GRAPHIQUE")
        
    def create_queue(self,queue=None) :
        if queue == None :
            self.queue = cl.CommandQueue(self.ctx)
        else : self.queue = queue
        
    def init_glob_var(self,item_weights,item_fitnesses,capacity,neg_overflow,solution_like) :
        self.nover = np.float32(neg_overflow)
        self.capa = np.int32(capacity)
        self.nbitem = len(item_fitnesses)
        

        self.weights_buf = cl.Buffer(self.ctx, self.mf.READ_ONLY | self.mf.COPY_HOST_PTR,
                                    hostbuf=np.pad(item_weights, (0, self.global_size - self.nbitem), constant_values=0))

        self.fitnesses_buf = cl.Buffer(self.ctx, self.mf.READ_ONLY | self.mf.COPY_HOST_PTR,
                                    hostbuf=np.pad(item_fitnesses, (0, self.global_size - self.nbitem), constant_values=0))

        buffersize = self.global_size * solution_like.dtype.itemsize #pour tabu et sol
        self.solution_buf = cl.Buffer(self.ctx, self.mf.READ_ONLY, size=buffersize)
        self.tabu_buf = cl.Buffer(self.ctx, self.mf.READ_ONLY, size=buffersize)
        cl.enqueue_fill_buffer(self.queue,self.tabu_buf,np.uint8(1),0,buffersize)
        # les calculs d'index se font par groupe.
        # [256] .. [256] -> dans le dernier y'en a que 2 en vrai, mais y'en a quand même 256(par exemple)
        # il faut par récupérer les valeurs aléatoires dans la mémoire donc
        # on remplis la liste tabou de 1 pour que tout ce qui n'est pas assigné soit filtré
        
        nb_g_padded = next_power_of_two(self.nb_groups)
        self.best_val_temp = np.full(nb_g_padded,-1048576.0,dtype=np.float32)
        self.best_vals_buf = cl.Buffer(self.ctx, self.mf.READ_WRITE | self.mf.COPY_HOST_PTR, hostbuf=self.best_val_temp)
        #lu puis utilisé
        self.best_indices_temp = np.full(nb_g_padded,-1,dtype=np.int32)
        self.best_indices_buf = cl.Buffer(self.ctx, self.mf.READ_WRITE | self.mf.COPY_HOST_PTR, hostbuf=self.best_indices_temp)
        #lu puis utilisé
        self.nb_group_pad = nb_g_padded
        
        #retour 2nd (1 unique bit)
        self.best_id_temp = np.zeros(1,dtype=np.int32)
        self.best_id_buf = cl.Buffer(self.ctx, self.mf.WRITE_ONLY, size=self.best_id_temp.nbytes)
        

    
    def compute(self,solution,poids,tabu_list) :      
        
        cl.enqueue_copy(self.queue, self.solution_buf, solution)
        cl.enqueue_copy(self.queue, self.tabu_buf, tabu_list)
        
        self.localcalc.compute_temp(
            self.queue, (self.global_size,), (self.local_size,),
            self.solution_buf, self.weights_buf, self.fitnesses_buf, self.tabu_buf,
            np.int32(poids), self.capa, self.nover,
            self.best_vals_buf, self.best_indices_buf
        )
        self.localcalc.reduce_max_global(
            self.queue, (self.nb_group_pad,), (self.nb_group_pad,),
            self.best_vals_buf, self.best_indices_buf,
            np.int32(self.nb_group_pad),
            self.best_id_buf
            )
        cl.enqueue_copy(self.queue, self.best_id_temp,self.best_id_buf)

        return self.best_id_temp[0]
        
    def compile_progs(self) :
        compute_local_temp = """
                    __kernel void compute_temp(
                        __global const char *solution,
                        __global const int *item_weights,
                        __global const int *item_fitnesses,
                        __global const char *tabu_list,
                        const int poids,
                        const int capacity,
                        const float overflow_cost,  // overflow_cost reste en float pour la précision
                        __global float *best_vals,     // [nb_groups]
                        __global int *best_indices   // [nb_groups]
                    ) {
                        int i = get_global_id(0);
                        int lid = get_local_id(0);
                        int group = get_group_id(0);
                        int lsize = get_local_size(0);
                        
                        __local float local_vals[256]; //creation de variables interne à chaque groupes
                        __local int local_indices[256];
                        
                        // Calcul de flip
                        int flip = 1 - 2 * solution[i];
                        // Calcul du poids après "flip" en entier
                        int flipped_weights = flip * item_weights[i] + poids;


                        float temp = flip * item_fitnesses[i];
                        //pour overflow
                        if (flipped_weights > capacity) {
                            temp -= (flipped_weights - capacity) * overflow_cost;
                        }

                        if (tabu_list[i]) {
                            // Utilisation d'une valeur minimale pour neutraliser les mouvements tabous
                            //les éléments du derniers groupes hors bornes entrent dans ce cas.
                            local_vals[lid] = -1048576.f; 
                            local_indices[lid] = -1;//opération pas ok.
                        } else {
                            local_vals[lid] = temp;//valeur locale : self
                            local_indices[lid] = i;//indice global
                        }

                        barrier(CLK_LOCAL_MEM_FENCE);//sync

                        // Réduction dans le groupe
                        for (int offset = lsize / 2; offset > 0; offset >>= 1) {
                            if (lid < offset) {
                                if (local_vals[lid] < local_vals[lid + offset]) {
                                    local_vals[lid] = local_vals[lid + offset];
                                    local_indices[lid] = local_indices[lid + offset];
                                }
                            }
                            barrier(CLK_LOCAL_MEM_FENCE);
                        }

                        // Thread 0 écrit le résultat du groupe
                        if (lid == 0) {
                            best_vals[group] = local_vals[0];
                            best_indices[group] = local_indices[0];
                        }
                        
                    }
                    
                    __kernel void reduce_max_global(
                        __global float *best_vals,  // Meilleures valeurs trouvées par chaque groupe
                        __global int *best_indices,  // Indices correspondants de chaque groupe
                        const int nbgroupes,
                        __global int *final_best_idx  // Résultat : indice du meilleur élément global
                    ) {
                        int i = get_global_id(0);  // Indice global pour l'agrégation

                        // Réduction des meilleures valeurs pour trouver le maximum global
                        for (int offset = nbgroupes / 2; offset > 0; offset >>= 1) {
                            if (i < offset) {
                                if (best_vals[i] < best_vals[i + offset]) {
                                    best_vals[i] = best_vals[i + offset];
                                    best_indices[i] = best_indices[i + offset];
                                }
                            }
                            barrier(CLK_GLOBAL_MEM_FENCE);  // Synchronisation après chaque étape
                        }

                        // Thread 0 écrit l'indice global du meilleur élément trouvé
                        if (i == 0) {
                            final_best_idx[0] = best_indices[0];
                        }
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
        
        self.oCLpc = openCLcompute(nbitem=self.sad.nbItem)
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


    def numpy_compare(self) : 
        flip = (1 - self.solution * 2)
        flipped_weights = flip * self.item_weights + self.poids
        
        temp = flip * self.item_fitnesses 
        overflow = flipped_weights > self.sad.capacity
        temp[overflow] -= ((flipped_weights[overflow] - self.sad.capacity) * self.OVERFLOW_COST).astype(int)
        
        mini = np.iinfo(np.int16).min
        # On neutralise les mouvements tabous
        temp[list(self.tabu_deque)] = mini
        
        return temp
    
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
            op = self.get_best_voisin()
            if (op <= -1) :
                #l'algo est bloqué
                break
        
            oldFit = self.true_fitness
            self.update_self_with_op(op)

            if (oldFit >= self.true_fitness) :
                #si c'est moins bien, on met dans la liste tabu
                self.tabu_pseudo_list[op]= 1
                self.tabu_deque.append(op)
                if (len(self.tabu_deque) > self.NB_TABU) :
                    poped = self.tabu_deque.popleft()
                    self.tabu_pseudo_list[poped] = 0
            
            if (self.sad.bestFitness <= self.true_fitness) :
                self.update_sad()
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