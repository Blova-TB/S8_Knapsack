import random
from SadObject import Sad

#TODO PENSER à remplacer sad.bestSolution par self.solution !!!!!

class Tabou_solver :  

    sad = None
    #taille max de la liste tabou
    NB_TABU = 20
    # liste tabu : liste des transformations interdites
    # Une opération c'est l'ajout ou la suppression d'un élément
    # comment la représenter : entier i = indice de l'élément ajouté ou supprimer
    tabu_list = []

    MAX_ITER = 100

    #solution courante
    solution = []
    fitness = 0
    poids = 0

    def __init__(self, sad : Sad) : 
        self.sad = sad
        (self.solution, self.fitness, self.poids) = self.create_rand_solution()
        self.update_sad

    def update_sad(self) : 
        if (self.poids <= self.sad.capacity) :
            self.sad.bestSolution = self.solution.copy()
            self.sad.bestFitness = self.fitness
        
    def create_rand_solution(self) :
        randSolut = [0]*self.sad.nbItem
        poids = 0
        fitness = 0
        while (poids < self.sad.capacity * 0.6) :
            i = random.randint(0,self.sad.nbItem-1)
            randSolut[i] += 1
            item = self.sad.listItems[i]
            poids += item.weight
            fitness += item.profit
        return randSolut, fitness, poids

    def get_voisin(self,solution,operation) :
        sol = solution.copy()
        sol[operation] = 1 - sol[operation]
        return sol
    
    def get_best_voisin(self, solution) : 
        best_voisin = []
        best_fitness = -1
        op=-1
        for i in range(0,self.sad.nbItem) :
            if (i in self.tabu_list) :
                continue
            voisin = self.get_voisin(solution,i)
            fitness = self.sad.calc_fitness(voisin)
            poids = self.sad.calc_poids(voisin)

            if (fitness > best_fitness and poids <= self.sad.capacity * 1.1) :
                best_fitness = fitness
                best_voisin = voisin
                op = i
                
        return best_voisin, best_fitness, op 
            
        
    def solve(self) : 
        #init boucle
        i = 0
        operations =[]
        for i in range(0, self.MAX_ITER) :
            (best_voisin, voisin_fitness,op) = self.get_best_voisin(self.solution)
            operations.append(op)
            
            delta = voisin_fitness - self.fitness
            #print(i,":",len(best_voisin),"/",self.sad.nbItem, " with a value of",voisin_fitness, " with the op ",op)
            self.update_self(best_voisin,voisin_fitness)#on met la solution courrante à jour
            
            if (delta <= 0) :
                #si c'est moins bien, on met dans la liste tabu
                self.tabu_list.append(op)
                if (len(self.tabu_list) > self.NB_TABU) :
                    self.tabu_list.pop(0)
            elif (self.sad.bestFitness <= self.fitness and self.poids <= self.sad.capacity) :
                self.update_sad()
        print("end of algo")

    def update_self(self, solution ,fitness) :
        self.solution = solution.copy()
        self.fitness = fitness
        self.poids = self.sad.calc_poids(self.solution)
    