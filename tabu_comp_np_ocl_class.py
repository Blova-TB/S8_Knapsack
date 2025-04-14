
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

seed = 1000
solver =  tbns.tabou_numpy_solver(sad,700,900,2.1,0.5,seed)
solver2 = tbcs.tabou_opencl2_solver(sad2,700,900,2.1,0.5,seed)
solver3 = tb2s.tabou2_solver(sad3,700,900,2.1,0.5,seed)

t = time.time()
rslt = solver.solve()
t2 = time.time()
rslt2 = solver2.solve()
t3 = time.time()
rslt3 = solver3.solve()
t4 = time.time()

print(f"prefect : {perfect}")#je peux plus retirer la faute maintenant
print("np     :",rslt[0],f"time {t2-t}")
print(f"ocl   : {rslt2[0]} time {t3-t2}")
print(f"class : {rslt3[0]} time {t4-t3}")
print("np",solver.poids,"kg, f=",solver.true_fitness)
print("ocl",solver2.poids,"kg, f =",solver2.true_fitness)
print("classique",solver3.poids,"jg  f=",solver3.true_fitness)

# THEORICAL ouput (il y a des seeds pour lesquelles tout les résultats sont identiques, ou différents... J'avoue qu'au final ça dépend )
# prefect : 64077  #
# np     : 47385 time 0.11
# ocl   : 46293 time 0.15
# class : 46293 time 12.239
# np 31693 kg, f= 47669.1
# ocl 31271 kg, f = 46293.3
# classique 31271 jg  f= 46293.3