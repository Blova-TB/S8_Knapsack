class SadItem:
    id = 0
    weight = 0
    profit = 0
    
    def __init__(self,_id,_weight,_profit):
        self.id = _id
        self.weight = _weight
        self.profit = _profit
    def __str__(self):
        return str(self.weight)+ "kg " + str(self.profit) + "$"
    def get_ratio(self):
        return self.profit/self.weight
class Sad:
    name = ""
    comment = ""
    probleme = ""
    capacity = 0
    nbItem = 0
    listItems = []
    bestSolution = []
    bestFitness = 0
    
    def __init__(self,_name,_comment,_probleme,_capacity,_nbItem,_listItems:list[SadItem],sort=False):
        self.name = _name
        self.comment = _comment
        self.probleme = _probleme
        self.capacity = _capacity
        self.nbItem = _nbItem
        self.listItems=_listItems
        if (sort):
            self.listItems.sort(
                key=lambda x: x.get_ratio(),
                reverse=True)
    
    def get_item(self,i:int):
        return self.listItems[i]
    
    def reinit(self) :
        self.bestSolution = [0]*self.nbItem
        self.bestFitness = 0
        
    def __str__(self) :
        retour = ""
        for item in self.listItems:
            retour += item.__str__() + '\n'
        return retour
    
    def calc_fitness(self, solution) : 
        fitness = 0
        for i in range(len(solution)) :
            item = self.listItems[i]
            fitness += item.profit * solution[i]
        return fitness 
    
    def calc_poids(self, solution) : 
        poids = 0
        for i in range(len(solution)) :
            poids += self.listItems[i].weight * solution[i]
        return poids
    
    def calc_fitness_poids(self,solution) :
        fitness = 0
        poids =0
        for i in range(len(solution)) :
            poids += self.listItems[i].weight * solution[i]
            fitness += self.listItems[i].profit * solution[i]
        return fitness, poids
    
    def describe_sol(self,solution) :
        desc = self.describe_entete_sol(solution)
        for i in range(len(solution)) :
            if solution[i] :
                item = self.listItems[i]
                desc += str(solution[i]) + "x"+str(item.id) + "\t: "
                desc += str(item.weight) + "kg\t" + str(item.profit) + '$\n'
        return desc
    
    def describe_entete_sol(self,solution) :
        (fit,poids) = self.calc_fitness_poids(solution)
        desc =  "fitness: "+str(fit)
        desc += "\n  poids: "+str(poids)+"/"+ str(self.capacity)+"\n"
        desc += " nb item:" + str(sum(solution))+"/"+str(self.nbItem)
        return desc