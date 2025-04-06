from tqdm import tqdm
from tools.SadObject import SadItem,Sad

def loadFromFile(path,sort_sad=False):
    fichier = open(path, "r")
    name = fichier.readline().split(":")[1].strip()
    comment = fichier.readline().split(":")[1].strip()
    probleme = fichier.readline().split(":")[1].strip()
    nbItems = int(fichier.readline().split(":")[1].strip())
    capacity = int(fichier.readline().split(":")[1].strip())

    fichier.readline()
    args = fichier.readline().split("[")[1].replace("]:","").replace("\n","").split(" ")
    for i in range(len(args)) :
        args[i] = "_"+args[i]
    
    listItems = []
    for i in tqdm(range(nbItems),desc="loading file",unit="lines",unit_scale=True):
        line = fichier.readline().split()
        argument = {args[i] : int(line[i]) for i in range(len(args))}
        listItems.append(SadItem(**argument))
    fichier.close()

    # print(name)
    # print(comment)
    # print(probleme)
    # print(nbItems)
    # print(capacity)
    # for i in listItems:
    #     print(i.id, i.weight, i.profit)
    
    return Sad(name, comment, probleme, capacity, nbItems, listItems,sort=sort_sad)

# Exemple :
# loadFromFile("Data/pi-12-100-1000-001.kna")