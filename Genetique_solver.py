import random
from Solver import Solver
from collections import deque
from testor import *
from SadObject import *
import parser
import tabou_solver as tbs
from MyIterator import *

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
        self.population = [[0]*self.sad.nbItem for i in range(self.nb_pop)]
        self.create_rand_population()
        
        test = self.calc_fitness_pop()
        for i in range(10):
            print(test[i])

    def create_rand_population(self):
        for i in range(self.nb_pop):
            for j in range(self.sad.nbItem):
                self.population[i][j] = random.getrandbits(1)

    def reproduction(self):
        print("reproduction")

    def croisement(self):
        print("croisement")

    def mutation(self):
        print("mutation")
        for i in range(self.population.__len__()):
            for j in range(self.population[i].__len__()):
                if(random.random()<self.mutation_rate):
                    if(self.population[i][j] == 1):
                        self.population[i][j] = 0
                    else:
                        self.population[i][j] = 1

    def calc_fitness(self,id):
        return sum((self.sad.listItems[i].profit if self.population[id][i] else 0) for i in range(self.sad.nbItem))

    def calc_fitness_pop(self):
        temp = []
        for i in range(self.nb_pop):
            temp.append(self.calc_fitness(i))
        return temp

    def affPop(self):
        for sol in self.population:
            print(sol)
        


sad = parser.loadFromFile("Data/pi-12-100-1000-001.kna")
test = Genetique_solver(sad,10,10,1,0.1,0)
test.affPop()
test.mutation()
test.affPop()

