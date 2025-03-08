from SadObject import SadItem,Sad

def loadFromFile(path):
    fichier = open(path, "r")
    name = fichier.readline().split(":")[1].strip()
    comment = fichier.readline().split(":")[1].strip()
    probleme = fichier.readline().split(":")[1].strip()
    nbItems = int(fichier.readline().split(":")[1].strip())
    capacity = int(fichier.readline().split(":")[1].strip())

    fichier.readline()
    fichier.readline()

    listItems = []
    for i in range(nbItems):
        line = fichier.readline().split()
        if (i%100 == 0) :
            print(line[0],end=" ")
        listItems.append(SadItem(int(line[0]), int(line[1]), int(line[2])))
    fichier.close()
    print()

    # print(name)
    # print(comment)
    # print(probleme)
    # print(nbItems)
    # print(capacity)
    # for i in listItems:
    #     print(i.id, i.weight, i.profit)
    
    return Sad(name, comment, probleme, capacity, nbItems, listItems)

# Exemple :
# loadFromFile("Data/pi-12-100-1000-001.kna")