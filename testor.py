import math

import numpy as np
from SadObject import Sad
from typing import Callable
from tqdm import tqdm
from Solver import Solver

from multiprocessing import Queue, Process
import os

def test_batch(q: Queue,manage_queue:Queue,solver : Solver, parameter : int, reinit_method : Callable[[Solver, int], Solver],size : int) :
    fitnesses = []
    for j in range(size) :
        solver = reinit_method(solver, parameter)
        solver.solve()
        fitnesses.append(solver.sad.bestFitness)
    q.put((parameter, np.average(fitnesses),math.sqrt(np.var(fitnesses))))
    manage_queue.put((True))


def manage_processes(resultQueue: Queue,solver : Solver, iterator, reinit_method : Callable[[Solver, int], Solver],group_size : int) :
    processes : list[Process]= []
    count_queue = Queue()
    process_count = 0
    for i in iterator :
        p = Process(
            target=test_batch,
            args=(resultQueue,count_queue, solver, i, reinit_method, group_size),
            )
        p.start()
        processes.append(p)
        
        #on évite de créer plus de process qu'on a de coeurs (sinon ça marche moins bien, d'expérience...)
        process_count += 1
        if(process_count >= os.cpu_count()) :
            count_queue.get()
            process_count -=1
        
    for p in processes :
        p.join()
        p.close()
    
    

class Testor : 
    def __init__(self, solver : Solver) :
        self._solver = solver  
    
    def test(self, iterator,solver_reinit_method : Callable[[Solver, int], Solver],group_size=1):
        queue = Queue()
        
        processMaker = Process(
            target=manage_processes,
            args=(queue, self._solver, iterator, solver_reinit_method, group_size),
            name="Knapsack - Process Manager"
            )
        processMaker.start()
            
        fitnessList = []
        rangeList = []
        variances = []
        unit = "sol" if (group_size == 1) else "batch"
        
        #on récupère les résultats
        for _ in tqdm(iterator,unit=unit, desc="calcul") :
            results=queue.get()
            fitnessList.append(results[1])
            rangeList.append(results[0])
            variances.append(results[2])
            
        #on attend la fin des process
        processMaker.join()
        processMaker.close()
    
        return (rangeList,fitnessList,variances)
    