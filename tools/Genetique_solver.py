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
    nb_iter : int
    nb_pop : int
    mutation_rate : float
    population : list[set]
    run_type : str
    list_proba_mutation : list[float]
    list_weight : list[int]
    list_fitness : list[int]

    def __init__(self, sad, nb_iter, nb_pop, mutation_rate, seed, run_type = "classic"):
        super().__init__(sad,seed)
        self.run_type = run_type
        self.nb_iter = nb_iter
        self.nb_pop = nb_pop
        self.mutation_rate = mutation_rate
        self.list_weight = [0]*self.nb_pop
        self.list_fitness = [0]*self.nb_pop
        self.init_list_proba_mutation()
        self.population = [set() for i in range(self.nb_pop)]
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
        # self.aff_pop_info_premier(10)
        return self.sad.bestSolution, self.sad.bestFitness
    
    def solve_new_mutation(self):
        for _ in range(self.nb_iter):
            self.croisement()
            # print("--> croisement done")
            # self.aff_pop_info_premier(10)
            self.mutation_equ()
            # print("--> mutation done")
            # self.aff_pop_info_premier(10)
            self.reproduction_with_new_mut()
            # print("--> reproduction done")
            # self.aff_pop_info_premier(10)
        # self.aff_pop_info_premier(10)
        return self.sad.bestSolution, self.sad.bestFitness



    def create_rand_population(self):
        for i in range(self.nb_pop):
            for j in range(self.sad_nbItem):
                if random.randint(0,1) == 1:
                    self.population[i].add(j)

    def create_rand_pop_weight(self,max_weight):
        for i in range(self.nb_pop):
            current_weight = 0
            nb_object = 0
            while(current_weight < max_weight and nb_object < self.sad_nbItem):
                rand = random.randint(0,self.sad_nbItem-1)
                while(rand in self.population[i]):
                    rand += 1
                    if(rand == self.sad_nbItem) : rand = 0
                self.population[i].add(rand)
                current_weight += self.item_weights[rand]

    def reproduction(self):
        # print("----------------------reproduction----------------------")
        
        coef = [0.0]*self.nb_pop
        coef_tot = 0
        for i in range(self.nb_pop):
            fitness, weight = self.calc_solut_fit_poids_set(self.population[i])
            if(fitness>self.sad.bestFitness and weight<self.sad_capacity):
                self.sad.bestSolution = self.population[i].copy()
                self.sad.bestFitness = fitness
                
                # print("new best :",fitness,"solution : ",self.population[i])

            coef[i] = self.calc_real_fitness(fitness,weight)
            coef_tot += coef[i]

        coef[0] = coef[0] / coef_tot
        for i in range(1,self.nb_pop):
            coef[i] = (coef[i] / coef_tot) + coef[i-1]
            
        new_pop = []

        for i in range(self.nb_pop):
            new_pop.append(self.population[np.searchsorted(coef, random.random())])

        self.population = new_pop

    def reproduction_with_new_mut(self):
        # print("----------------------reproduction----------------------")
        
        coef = [0.0]*self.nb_pop
        coef_tot = 0
        for i in range(self.nb_pop):
            # self.list_fitness[i], self.list_weight[i] = self.calc_solut_fit_poids_set(self.population[i])
            if(self.list_fitness[i]>self.sad.bestFitness and self.list_weight[i]<self.sad_capacity):
                self.sad.bestSolution = self.population[i].copy()
                self.sad.bestFitness = self.list_fitness[i]
            coef[i] = self.calc_real_fitness(self.list_fitness[i],self.list_weight[i])
            coef_tot += coef[i]

        coef[0] = coef[0] / coef_tot
        for i in range(1,self.nb_pop):
            coef[i] = (coef[i] / coef_tot) + coef[i-1]
            
        new_pop = []

        for i in range(self.nb_pop):
            new_pop.append(self.population[np.searchsorted(coef, random.random())])

        self.population = new_pop


    def croisement(self):
        # print("-----------------------croisement-----------------------")
        
        random.shuffle(self.population)

        half = self.nb_pop // 2

        for i in range(0,half):
            j = half + i

            cut_index = random.randint(1,self.sad_nbItem-2)

            sol1 = set()
            sol2 = set()

            for k in self.population[i]:
                if(k < cut_index):
                    sol1.add(k)
                else:
                    sol2.add(k)
            for k in self.population[j]:
                if(k < cut_index):
                    sol2.add(k)
                else:
                    sol1.add(k)

            self.population[i] = sol1
            self.population[j] = sol2

    def slow_mutation(self):
        # print("------------------------mutation------------------------")
        for i in range(self.nb_pop):
            for j in range(self.sad_nbItem):
                if(random.random()<self.mutation_rate):
                    if (j in self.population[i]):
                        self.population[i].remove(j)
                    else:
                        self.population[i].add(j)

    def mutation(self):
        # print("------------------------mutation------------------------")
        for i in range(self.nb_pop):
            nb_mutation = np.searchsorted(self.list_proba_mutation, random.random())
            muted_set = set()
            for _ in range(nb_mutation):
                rand = random.randint(0,self.sad_nbItem-1)
                while(rand in muted_set):
                    rand = random.randint(0,self.sad_nbItem-1)
                if (rand in self.population[i]):
                    self.population[i].remove(rand)
                else:
                    self.population[i].add(rand)
                muted_set.add(rand)

    def mutation_equ(self):
        # print("------------------------mutation-equ--------------------")            

        for i in range(self.nb_pop):
            self.list_weight[i], self.list_fitness[i] = self.calc_solut_fit_poids_set(self.population[i])
            
            nb_mutation = np.searchsorted(self.list_proba_mutation, random.random())
            nb_item_take = len(self.population[i])
            mutation_sub = set()
            mutation_add = set()
            
            for _ in range(nb_mutation):
                if(self.list_weight[i] > self.sad_capacity):
                    if(len(mutation_sub) == nb_item_take):
                        break
                    rand = random.randint(0, nb_item_take)
                    while(rand in mutation_sub):
                        rand = random.randint(0, nb_item_take)
                    mutation_sub.add(rand)
                    self.list_weight[i] -= self.item_weights[rand]
                    self.list_fitness[i] -= self.item_fitnesses[rand]
                else:
                    rand = random.randint(0, self.sad_nbItem - 1 - nb_item_take)
                    if(len(mutation_add) == self.sad_nbItem - nb_item_take):
                        break
                    while(rand in mutation_add):
                        rand = random.randint(0, self.sad_nbItem - 1 - nb_item_take)
                    mutation_add.add(rand)
                    self.list_weight[i] += self.item_weights[rand]
                    self.list_fitness[i] += self.item_fitnesses[rand]

            index_nb_item_take = 0
            index_nb_item_not_take = 0

            for j in range(self.sad_nbItem):
                if(j in self.population[i]):
                    if(index_nb_item_take in mutation_sub):
                        self.population[i].remove(j)
                    index_nb_item_take += 1
                else:
                    if(index_nb_item_not_take in mutation_add):
                        self.population[i].add(j)
                    index_nb_item_not_take += 1

    def calc_solut_fit_poids_set(self,sol):
        fit = 0
        poids = 0
        for i in sol:
            fit += self.item_fitnesses[i]
            poids += self.item_weights[i]
        return fit, poids

        

    def aff_pop(self):
        for sol in self.population:
            print(sol)

    def aff_pop_info(self):
        print("--------------------------------------------------aff_pop_info--------------------------------------------------")
        for sol in self.population:
            (fitness,weight) = self.sad.calc_solut_fit_poids_set(sol)
            print("|",id(sol),"| fitness : ", fitness,"weight : ", weight, "real fitness : ", self.calc_real_fitness(fitness,weight), "|")

    def aff_pop_info_premier(self,n):
        print("--------------------------------------------------aff_pop_info--------------------------------------------------")
        i = 0
        for sol in self.population:
            (fitness,weight) = self.sad.calc_solut_fit_poids_set(sol)
            print("|",id(sol),"| fitness : ", fitness,"weight : ", weight, "real fitness : ", self.calc_real_fitness(fitness,weight), "|")
            i += 1
            if(i>n):
                break
        
    def tab_to_int(self,sol):
        res = 0
        for i in range(self.sad_nbItem):
            res += 2**i * sol[i]
        return res
    
    def calc_real_fitness(self,fitness,weight):
        return max(fitness - 3 * max(weight - self.sad_capacity,0),1)
    
    def init_list_proba_mutation(self):
        self.list_proba_mutation = [(1.0 - self.mutation_rate) ** self.sad_nbItem]
        reretest = (1.0 - self.mutation_rate) ** self.sad_nbItem
        combinaisons = 1
        i = 0
        while (self.list_proba_mutation[-1] != 1.0):
            i += 1
            combinaisons = combinaisons * (self.sad_nbItem-i+1)/i
            reretest = reretest * (self.mutation_rate) / (1.0 - self.mutation_rate)
            self.list_proba_mutation.append(self.list_proba_mutation[i-1] + combinaisons * reretest)
            if (self.list_proba_mutation[i] == self.list_proba_mutation[i-1]):
                self.list_proba_mutation[i] = 1.0
        # print("list_proba_mutation : ",self.list_proba_mutation)
        # print("nb_item : ",self.sad_nbItem, "mutation_rate : ",self.mutation_rate)

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