import cProfile
import parser
import random
from Genetique_solver import *


# sad = parser.loadFromFile("Data/pi-15-10000-1000-001.kna")
sad = parser.loadFromFile("Data/pi-12-10000-1000-001.kna")
solver = Genetique_solver(sad,5,50,0.001,1)
sol,fit=solver.solve()
print(sad.describe_entete_sol(sol))

# for i in range(1):
#     test = Genetique_solver(sad,50,50,0.0005,i)
#     sol,fit=test.solve()
#     print(sad.describe_entete_sol(sol))
#     # cProfile.run('test.solve()')

