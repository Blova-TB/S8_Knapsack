import random
from tools.Solver import *
from collections import deque
from tools.testor import *
from tools.SadObject import *
import tools.tabou_solver as tbs
from tools.MyIterator import *

import numpy as np
import matplotlib.pyplot as plt


class Genetique_solver(Solver):
    seed : int
    sad : Sad
    nb_iter : int
    nb_pop : int
    mutation_rate : float
    population : list[list[bool]]

    def __init__(self, sad, nb_iter, nb_pop, mutation_rate, seed, run_type = "classic"):
        super().__init__(sad,seed)
        self.run_type = run_type
        self.nb_iter = nb_iter
        self.nb_pop = nb_pop
        self.mutation_rate = mutation_rate
        self.init_list_proba_mutation()
        self.population = [[0]*self.sad.nbItem for i in range(self.nb_pop)]
        self.pop_fitness = [0]*self.nb_pop
        self.pop_weight = [0]*self.nb_pop
        self.create_rand_pop_weight(self.sad.capacity)

    def solve(self):
        match(self.run_type):
            case "classic":
                return self.solve_classic()
            case "new_mutation":
                return self.solve_new_mutation()
            case default:
                raise ValueError(f"Unknown run type: {self.run_type}")
    
    def solve_classic(self):
        for _ in range(self.nb_iter):
            # print("iteration : ",i)
            self.reproduction()
            # print("--> reproduction done")
            # self.aff_pop_info()
            self.croisement()
            # print("--> croisement done")
            # self.aff_pop_info()
            self.mutation()
            # print("--> mutation done")
            # self.aff_pop_info()
        return self.sad.bestSolution, self.sad.bestFitness
    
    def solve_new_mutation(self):
        for _ in range(self.nb_iter):
            self.reproduction()
            self.croisement()
            self.mutation_equ()
        return self.sad.bestSolution, self.sad.bestFitness



    def create_rand_population(self):
        for i in range(self.nb_pop):
            for j in range(self.sad.nbItem):
                self.population[i][j] = random.getrandbits(1)

    def create_rand_pop_weight(self,max_weight):
        for i in range(self.nb_pop):
            current_weight = 0
            nb_object = 0
            while(current_weight < max_weight and nb_object < self.sad.nbItem):
                rand = random.randint(0,self.sad.nbItem-1)
                while(self.population[i][rand] == 1):
                    rand += 1
                    if(rand == self.sad.nbItem) : rand = 0
                self.population[i][rand] = 1
                current_weight += self.sad.get_item(rand).weight

    def reproduction(self):
        # print("----------------------reproduction----------------------")
        
        coef = [0.0]*self.nb_pop
        coef_tot = 0
        for i in range(self.nb_pop):
            (fitness,weight) = self.sad.calc_fitness_poids(self.population[i])
            if(fitness>self.sad.bestFitness and weight<self.sad.capacity):
                self.sad.bestSolution = self.population[i].copy()
                self.sad.bestFitness = fitness
                
                # print("new best :",fitness,"solution : ",self.population[i])


            coef[i] = self.calc_real_fitness(fitness,weight)
            coef_tot += coef[i]

        coef[0] = coef[0] / coef_tot
        for i in range(1,self.nb_pop):
            coef[i] = (coef[i] / coef_tot) + coef[i-1]
            

        new_pop = [[0]*self.sad.nbItem for i in range(self.nb_pop)]
        
        rand_list = [random.random() for i in range(self.nb_pop)]
        list.sort(rand_list)
        rand_list.append(999)
        # pour sortir de la boucle while a la fin

        index = 0
        # print("rand_list : ",rand_list)
        # print("coef : ",coef)
        for i in range(self.nb_pop):
            while(rand_list[index]<coef[i]):
                new_pop[index]=self.population[i].copy()
                index += 1

        self.population = new_pop

    def croisement(self):
        # print("-----------------------croisement-----------------------")
        random.shuffle(self.population)
        for i in range(0,self.nb_pop - 1,2):
            cut_index = random.randint(1,self.sad.nbItem-2)
            self.population[i][cut_index:],self.population[i+1][cut_index:] = self.population[i+1][cut_index:],self.population[i][cut_index:]

    def slow_mutation(self):
        # print("------------------------mutation------------------------")
        for i in range(self.nb_pop):
            for j in range(self.sad.nbItem):
                if(random.random()<self.mutation_rate):
                    self.population[i][j] = 1 - self.population[i][j]

    def mutation(self):
        # print("------------------------mutation------------------------")
        for i in range(self.nb_pop):
            nb_mutation = np.searchsorted(self.list_proba_mutation, random.random())
            muted_set = set()
            for j in range(nb_mutation):
                rand = random.randint(0,self.sad.nbItem-1)
                while(rand in muted_set):
                    rand = random.randint(0,self.sad.nbItem-1)
                self.population[i][rand] = 1 - self.population[i][rand]
                muted_set.add(rand)

    def mutation_equ(self):
        # print("------------------------mutation-equ--------------------")
        for i in range(self.nb_pop):
            nb_mutation = np.searchsorted(self.list_proba_mutation, random.random())
            nb_item_take = 0
            for j in range(self.sad.nbItem):
                if(self.population[i][j] == 1):
                    nb_item_take += 1

            mutation_sub = set()
            mutation_add = set()

            for _ in range(nb_mutation):
                if(random.random() < 0.5): # mutation add
                    if(len(mutation_add) < self.sad.nbItem - nb_item_take):
                        rand = random.randint(0, self.sad.nbItem - 1 - nb_item_take)
                        while(rand in mutation_add):
                            rand = random.randint(0, self.sad.nbItem - 1 - nb_item_take)
                        mutation_add.add(rand)

                else: # mutation sub
                    if(len(mutation_sub) < nb_item_take):
                        rand = random.randint(0, nb_item_take - 1)
                        while(rand in mutation_sub):
                            rand = random.randint(0, nb_item_take - 1)
                        mutation_sub.add(rand)

            index_nb_item_take = 0
            index_nb_item_not_take = 0

            for j in range(self.sad.nbItem):
                if(self.population[i][j] == 1):
                    if(index_nb_item_take in mutation_sub):
                        self.population[i][j] = 0
                    index_nb_item_take += 1
                else:
                    if(index_nb_item_not_take in mutation_add):
                        self.population[i][j] = 1
                    index_nb_item_not_take += 1

    def aff_pop(self):
        for sol in self.population:
            print(sol)

    def aff_pop_info(self):
        print("--------------------------------------------------aff_pop_info--------------------------------------------------")
        for sol in self.population:
            (fitness,weight) = self.sad.calc_fitness_poids(sol)
            print("|",id(sol),"| fitness : ", fitness,"weight : ", weight, "real fitness : ", self.calc_real_fitness(fitness,weight), "|")

    def aff_pop_info_premier(self,n):
        print("--------------------------------------------------aff_pop_info--------------------------------------------------")
        i = 0
        for sol in self.population:
            (fitness,weight) = self.sad.calc_fitness_poids(sol)
            print("|",id(sol),"| fitness : ", fitness,"weight : ", weight, "real fitness : ", self.calc_real_fitness(fitness,weight), "|")
            i += 1
            if(i>n):
                break
        
    def tab_to_int(self,sol):
        res = 0
        for i in range(self.sad.nbItem):
            res += 2**i * sol[i]
        return res
    
    def calc_real_fitness(self,fitness,weight):
        return max(fitness - 2 * max(weight - self.sad.capacity,0),1)
    
    def init_list_proba_mutation(self):
        self.list_proba_mutation = [(1.0 - self.mutation_rate) ** self.sad.nbItem]
        reretest = (1.0 - self.mutation_rate) ** self.sad.nbItem
        combinaisons = 1
        i = 0
        while (self.list_proba_mutation[-1] != 1.0):
            i += 1
            combinaisons = combinaisons * (self.sad.nbItem-i+1)/i
            reretest = reretest * (self.mutation_rate) / (1.0 - self.mutation_rate)
            self.list_proba_mutation.append(self.list_proba_mutation[i-1] + combinaisons * reretest)
            if (self.list_proba_mutation[i] == self.list_proba_mutation[i-1]):
                self.list_proba_mutation[i] = 1.0
        # print("list_proba_mutation : ",self.list_proba_mutation)
        # print("nb_item : ",self.sad.nbItem, "mutation_rate : ",self.mutation_rate)

def new_gen_nb_iter(solver:Genetique_solver, nb_iter:int) -> Genetique_solver:
    return Genetique_solver(solver.sad, nb_iter, solver.nb_pop, solver.mutation_rate, solver.seed +1 , solver.run_type)

def new_gen_nb_pop(solver:Genetique_solver, nb_pop:int) -> Genetique_solver:
    return Genetique_solver(solver.sad, solver.nb_iter, nb_pop, solver.mutation_rate, solver.seed +1 , solver.run_type)

def new_gen_mutation_rate(solver:Genetique_solver, mutation_rate:float) -> Genetique_solver:
    return Genetique_solver(solver.sad, solver.nb_iter, solver.nb_pop, mutation_rate, solver.seed +1 , solver.run_type)

class variateur_genetique : 
    def nombre_iterations() :
        return new_gen_nb_iter, "fitness en fonction du nombre d'itérations"
    def nombre_population() :
        return  new_gen_nb_pop, "fitness en fonction du nombre d'individus dans la population"
    def mutation_rate() :
        return new_gen_mutation_rate, "fitness en fonction de la probabilité de mutation"    

# sad = parser.loadFromFile("Data/pi-12-100-1000-001.kna")
# test = Genetique_solver(sad,10,100,0.01,2)
# sol,fit=test.solve()
# print(sad.describe_entete_sol(sol))