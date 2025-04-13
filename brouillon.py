
import tools.testor as testor
import tools.tabou2_solver as tb2s
import tools.tabou_numpy_solver as tbns
import tools.tabou_opencl2_solver as tbcs
import tools.parser as parser
import tools.Other_solver as ots
from tools.MyIterator import *
import cProfile
import time

sad = parser.loadFromFile("DATA/pi-13-10000-1000-001.kna")
sad2 = parser.loadFromFile("DATA/pi-13-10000-1000-001.kna")
sad3 = parser.loadFromFile("DATA/pi-13-10000-1000-001.kna")
perfect = ots.Other_solver(sad).solve()[0]

seed = int(time.time()*10**10)
solver = tbns.tabou_numpy_solver(sad,700,2000,1.8,0.1,seed)
solver2 = tbcs.tabou_opencl_solver(sad2,700,900,1.8,0.5,seed)
solver3 = tbns.tabou_numpy_solver(sad3,1000,900,2.074,0.5,seed)
# print("numpy")
# cProfile.run("solver.solve()")
# print("openCL")
# cProfile.run("solver2.solve()")
# time.sleep(0.1)

result = []
t = time.time()
rslt = solver.solve()
t2 = time.time()
rslt2 = solver2.solve()
t3 = time.time()
rslt3 = solver3.solve()
t4 = time.time()

print(f"prefect : {perfect}")
print("np : ",rslt[0],f"time {t2-t}")
print(f"ocl : {rslt2[0]} time {t3-t2}")
print(f"classique :{rslt3[0]} time {t4-t3}")
print("np",solver.poids,"kg/",solver.sad.capacity,", f=",solver.true_fitness)
print("ocl",solver2.poids,"kg, f =",solver2.true_fitness)
print("classique",solver3.poids,"jg  f=",solver3.true_fitness)