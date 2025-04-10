from matplotlib import pyplot as plt
import numpy as np
from tools.SadObject import Sad
from typing import Callable
from tqdm import tqdm
from tools.Solver import Solver

from multiprocessing import Queue, Process
import os


def graph_test_result(test_result,solution_optimale:int = None,title="Graph sans titre") :
    graph_result(test_result[0],test_result[1],test_result[2],title,opti=solution_optimale,other=test_result[3])


def graph_result(x,y,err,title,opti:int=None,other=[]) :
    fig = plt.figure()
    ax = fig.add_subplot()
    ax.set_title(title)
    ax.errorbar(x, y,yerr=err,fmt=".",linewidth=0.75)
    if(opti) :
        ax.axline((min(x),opti),(max(x),opti))
    if (len(other) == len(x)) :
        ax.plot(x,other,"r+")
    ax.autoscale()
    plt.show()


def plot_full_colored_matrix(matrix,x_ticks,y_ticks,title1="x",title2="y",title="",print_data=True,print_fitness_values=True):
    """
    Affiche une heatmap remplissant toute la surface, avec les couleurs
    correspondant aux valeurs de la matrice.
    """
    if print_data:
        print("matrix = ", matrix)
        print("x_ticks = ", list(x_ticks))
        print("y_ticks = ", list(y_ticks))
        print("title1 = \"", title1, "\"")
        print("title2 = \"", title2, "\"")
        print("title = \"", title, "\"")

    matrix = np.array(matrix)
    n, m = matrix.shape

    fig = plt.figure(figsize=(8, 8))
    ax = plt.gca()
    im = plt.imshow(matrix, cmap='coolwarm')
    plt.colorbar(im, label="fitness moyenne")
    plt.title(title)

    if print_fitness_values:
        for i in range(n):
            for j in range(m):
                plt.text(j, i, str(round(matrix[i][j])), ha='center', va='center', color='white', fontsize=5, fontweight='bold')

    ax.set_xticks(range(len(x_ticks)))
    ax.set_xticklabels(x_ticks)
    ax.set_yticks(range(len(y_ticks)))
    ax.set_yticklabels(y_ticks)

    ax.set_aspect('equal')

    ax.set_xlabel(title1)
    ax.set_ylabel(title2)

    plt.xticks(rotation=90)
    
    plt.tight_layout()
    plt.show()

def test_batch(q: Queue,manage_queue:Queue,solver : Solver, parameter : int, reinit_method : Callable[[Solver, int], Solver],size : int) :
    fitnesses = []
    for j in range(size) :
        solver = reinit_method(solver, parameter)
        solver.solve()
        fitnesses.append(solver.sad.bestFitness)
    avg = np.mean(fitnesses)
    median = int(np.median(fitnesses))
    down_pct = int(np.percentile(fitnesses,80)) - median
    up_pct = median - int(np.percentile(fitnesses,20))
    manage_queue.put((True))
    q.put((parameter,median,[up_pct,down_pct],avg))
    


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
            
        fitnessMedianeList = []
        rangeList = []
        erreure = [[],[]]
        avgFitnesses = []
        unit = "sol" if (group_size == 1) else "batch"
        #on récupère les résultats
        for _ in tqdm(iterator,unit=unit, desc="calcul") :
            
            results=queue.get()
            fitnessMedianeList.append(results[1])
            rangeList.append(results[0])
            err = results[2]
            erreure[0].append(err[0])
            erreure[1].append(err[1])
            avgFitnesses.append(results[3])
            
        #on attend la fin des process
        processMaker.join()
        processMaker.close()
    
        return (rangeList,fitnessMedianeList,erreure,avgFitnesses)
    