#pour dev
from testor import *
from SadObject import *
import parser
import tabou_solver as tbs
from MyIterator import *

import numpy as np
import matplotlib.pyplot as plt
import math

def increment(i) :
    return i+1

def main():
    sad = parser.loadFromFile("Data/pi-12-1000-1000-001.kna")

    test = Testor(tbs.Tabou_solver(sad,iter_max=1502))

    iterator = MyIterator(986, 1002, increment)

    (x,y,err) = test.test(iterator,tbs.reinit_tabu_list,10)
    
    fig, ax = plt.subplots()

    ax.set(xlim=(0, int(max(x)*1.025)+1), ylim=(0,int(max(np.add(y,err))*1.025)+1))

    ax.errorbar(x, y,yerr=err,fmt=".",linewidth=0.75)
    ax.set_title("fitness en fonction de la taille de la liste TABU")
    plt.show(block=True)

if __name__ == '__main__':
    main()
