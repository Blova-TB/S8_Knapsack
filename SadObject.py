class SadItem:
    id = 0
    weight = 0
    profit = 0
    
    def __init__(self,_id,_weight,_profit):
        self.id = _id
        self.weight = _weight
        self.profit = _profit

class Sad:
    name = ""
    comment = ""
    capacity = 0
    nbItem = 0
    listItems = []
    bestSolution = []
    def __init__(self,_name,_comment,_capacity,_nbItem,_listItems):
        self.name = _name
        self.comment = _comment
        self.capacity = _capacity
        self.nbItem = _nbItem
        self.listItems = _listItems
        