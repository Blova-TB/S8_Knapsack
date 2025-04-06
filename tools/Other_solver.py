from tools.Solver import Solver

from ortools.algorithms.python import knapsack_solver

class Other_solver(Solver) :
    
    def __init__(self, sad):
        profits = []
        weights = [[]]
        self.capacity = [sad.capacity]
        for item in sad.listItems :
            profits.append(item.profit)
            weights[0].append(item.weight)
        self.solver = knapsack_solver.KnapsackSolver(knapsack_solver.KNAPSACK_DIVIDE_AND_CONQUER_SOLVER,"1D solver")
        self.solver.init(profits,weights,self.capacity)
        
    def solve(self):
        profit = self.solver.solve()
        return profit, self.solver.is_solution_optimal()
    
    def get_solution(self) :
        liste = []
        for i in range(self.capacity[0]-1) :
            try :
                liste.append(self.solver.best_solution_contains(i))
            except:
                liste.append(False)
                break
        
                
        return liste