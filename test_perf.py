import cProfile
import parser
import random
from Genetique_solver import *

sad = parser.loadFromFile("Data/pi-15-1000-1000-001.kna")

for i in range(10):
    test = Genetique_solver(sad,50,50,1,0.0005,i)
    sol,fit=test.run()
    print(sad.describe_entete_sol(sol))
    cProfile.run('test.run()')