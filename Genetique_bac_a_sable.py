import cProfile
import tools.parser as parser
import random
from tools.Genetique_solver import *
import time

sad = parser.loadFromFile("Data/pi-13-1000-1000-001.kna")

nb_iter = 100
nb_pop = 200
mutation_rate = 0.00055
seed = 1
methode = "classic"

solver = Genetique_solver(sad,nb_iter,nb_pop,mutation_rate,seed,methode)
solver.solve()
    
    
            # pour afficher les 10 premiers individus de la population
solver.aff_pop_info_premier(10)

            # pour afficher les informations sur la solution trouvé
print(solver.sad.describe_entete_sol_set(solver.sad.bestSolution))

            # pour afficher la solution trouvée
print("\nsolution:", solver.sad.bestSolution,"\n")

            # pour analyser les performances
cProfile.run("solver.solve()")