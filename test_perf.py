import cProfile
import tools.parser as parser
import random
from tools.Genetique_solver import *
import time

# sad = parser.loadFromFile("Data/pi-15-10000-1000-001.kna")
sad = parser.loadFromFile("Data/pi-12-10000-1000-001.kna")


for i in range(10) :
    clock_start = time.time()
    solver = Genetique_solver(sad,300,200,0.0001,i)
    sol,fit=solver.solve()
    print("fit",i,":",fit)
    print("time",i,":",time.time()-clock_start)
# cProfile.run('sol,fit=solver.solve()')
print(sad.describe_entete_sol_set(sol))


#          2009809 function calls (2009808 primitive calls) in 25.120 seconds
#    Ordered by: standard name

#    ncalls  tottime  percall  cumtime  percall filename:lineno(function)
#         1    0.000    0.000   25.078   25.078 <string>:1(<module>)
#       300    0.925    0.003    1.046    0.003 Genetique_solver.py:121(croisement)
#       300    0.115    0.000    0.554    0.002 Genetique_solver.py:135(mutation)
#     60000    0.027    0.000    0.050    0.000 Genetique_solver.py:213(calc_real_fitness)
#         1    0.042    0.042   25.078   25.078 Genetique_solver.py:33(solve)
#         1    0.001    0.001    5.069    5.069 Genetique_solver.py:42(solve_classic)
#       300    1.931    0.006   23.395    0.078 Genetique_solver.py:82(reproduction)
#     60000   21.003    0.000   21.010    0.000 SadObject.py:62(calc_fitness_poids)




#          1949809 function calls (1949808 primitive calls) in 24.957 seconds

#    Ordered by: standard name

#    ncalls  tottime  percall  cumtime  percall filename:lineno(function)
#         1    0.000    0.000   24.917   24.917 <string>:1(<module>)
#       300    0.917    0.003    1.039    0.003 Genetique_solver.py:118(croisement)
#       300    0.114    0.000    0.563    0.002 Genetique_solver.py:132(mutation)
#     60000    0.026    0.000    0.050    0.000 Genetique_solver.py:210(calc_real_fitness)
#         1    0.042    0.042   24.917   24.917 Genetique_solver.py:30(solve)
#         1    0.001    0.001    4.916    4.916 Genetique_solver.py:39(solve_classic)
#       300    1.931    0.006   23.253    0.078 Genetique_solver.py:79(reproduction)
#     60000   20.852    0.000   20.852    0.000 Solver.py:22(calc_short_solut_fit_poids)




#          10024280 function calls in 5.775 seconds
#    Ordered by: standard name

#    ncalls  tottime  percall  cumtime  percall filename:lineno(function)
#         1    0.000    0.000    5.774    5.774 <string>:1(<module>)
#       300    1.297    0.004    2.344    0.008 Genetique_solver.py:118(croisement)
#       300    0.110    0.000    0.543    0.002 Genetique_solver.py:155(mutation)
#     60000    0.756    0.000    0.756    0.000 Genetique_solver.py:206(calc_solut_fit_poids_set)
#     60000    0.020    0.000    0.038    0.000 Genetique_solver.py:240(calc_real_fitness)
#         1    0.000    0.000    5.774    5.774 Genetique_solver.py:30(solve)
#         1    0.002    0.002    5.774    5.774 Genetique_solver.py:39(solve_classic)
#       300    1.938    0.006    2.885    0.010 Genetique_solver.py:80(reproduction)
#     60000    0.007    0.000    0.007    0.000 fromnumeric.py:1328(_searchsorted_dispatcher)
#     60000    0.024    0.000    0.279    0.000 fromnumeric.py:1332(searchsorted)
#     60000    0.069    0.000    0.200    0.000 fromnumeric.py:40(_wrapit)
#     60000    0.048    0.000    0.255    0.000 fromnumeric.py:53(_wrapfunc)
#     89988    0.046    0.000    0.073    0.000 random.py:242(_randbelow_with_getrandbits)
#     89988    0.064    0.000    0.162    0.000 random.py:291(randrange)
#     89988    0.027    0.000    0.189    0.000 random.py:332(randint)
#    269964    0.025    0.000    0.025    0.000 {built-in method _operator.index}
#         1    0.000    0.000    5.775    5.775 {built-in method builtins.exec}
#    120000    0.014    0.000    0.014    0.000 {built-in method builtins.getattr}
#    120000    0.019    0.000    0.019    0.000 {built-in method builtins.max}
#     60000    0.072    0.000    0.072    0.000 {built-in method numpy.asarray}
#   8344482    0.999    0.000    0.999    0.000 {method 'add' of 'set' objects}
#       300    0.000    0.000    0.000    0.000 {method 'append' of 'list' objects}
#     89988    0.011    0.000    0.011    0.000 {method 'bit_length' of 'int' objects}
#     60009    0.142    0.000    0.142    0.000 {method 'copy' of 'set' objects}
#         1    0.000    0.000    0.000    0.000 {method 'disable' of '_lsprof.Profiler' objects}
#    147493    0.016    0.000    0.016    0.000 {method 'getrandbits' of '_random.Random' objects}
#    120000    0.013    0.000    0.013    0.000 {method 'random' of '_random.Random' objects}
#       875    0.000    0.000    0.000    0.000 {method 'remove' of 'set' objects}
#     60000    0.051    0.000    0.051    0.000 {method 'searchsorted' of 'numpy.ndarray' objects}
#       300    0.004    0.000    0.004    0.000 {method 'sort' of 'list' objects}





# fit 0 : 42641
# time 0 : 3.7512810230255127
# fit 1 : 42724
# time 1 : 3.303913116455078
# fit 2 : 42299
# time 2 : 3.355724334716797
# fit 3 : 42351
# time 3 : 3.3609275817871094
# fit 4 : 42285
# time 4 : 3.2941291332244873
# fit 5 : 42928
# time 5 : 3.339163303375244
# fit 6 : 42586
# time 6 : 3.4079408645629883
# fit 7 : 42209
# time 7 : 3.252763509750366
# fit 8 : 42337
# time 8 : 3.1334524154663086
# fit 9 : 42582
# time 9 : 3.122241258621216