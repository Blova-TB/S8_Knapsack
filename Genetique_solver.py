import random
from Solver import Solver
from collections import deque
from testor import *
from SadObject import *
import tabou_solver as tbs
from MyIterator import *
import parser

import numpy as np
import matplotlib.pyplot as plt


class Genetique_solver(Solver):
    seed : int
    sad : Sad
    nb_iter : int
    nb_pop : int
    nb_crossing_points : int
    mutation_rate : float
    population : list[list[bool]]

    def __init__(self, sad: Sad, nb_iter, nb_pop, nb_crossing_points, mutation_rate, seed):
        self.seed = seed
        random.seed(self.seed)
        super().__init__(sad)
        self.nb_iter = nb_iter
        self.nb_pop = nb_pop
        self.nb_crossing_points = nb_crossing_points
        self.mutation_rate = mutation_rate
        self.init_list_proba_mutation()
        self.population = [[0]*self.sad.nbItem for i in range(self.nb_pop)]
        self.pop_fitness = [0]*self.nb_pop
        self.pop_weight = [0]*self.nb_pop
        self.create_rand_pop_weight(self.sad.capacity)

    def run(self):
        for i in range(self.nb_iter):
            # print("iteration : ",i)
            self.reproduction()
            # print("reproduction done")
            # self.aff_pop_info()
            self.croisement()
            # print("croisement done")
            # self.aff_pop_info()
            self.mutation()
            # print("mutation done")
            # self.aff_pop_info()
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
        for i in range(0,self.nb_pop,2):
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

    def aff_pop(self):
        for sol in self.population:
            print(sol)

    def aff_pop_info(self):
        print("--------------------------------------------------aff_pop_info--------------------------------------------------")
        for sol in self.population:
            (fitness,weight) = self.sad.calc_fitness_poids(sol)
            # print("|",self.tab_to_int(sol),"| fitness : ", fitness,"weight : ", weight, "real fitness : ", self.calc_real_fitness(fitness,weight), "|")
            print("|",id(sol),"| fitness : ", fitness,"weight : ", weight, "real fitness : ", self.calc_real_fitness(fitness,weight), "|")

        
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


# sad = parser.loadFromFile("Data/pi-12-100-1000-001.kna")
# test = Genetique_solver(sad,10,100,1,0.01,1)