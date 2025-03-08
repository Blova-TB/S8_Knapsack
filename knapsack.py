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
    return i+20

def main():
    sad = parser.loadFromFile("Data/pi-12-1000-1000-001.kna")

    test = Testor(tbs.Tabou_solver(sad,iter_max=100,tabu_size=10))

    iterator = MyIterator(1, 1002, increment)

    (x,y,err) = test.test(iterator,tbs.reinit_tabu_list,2)
    
    fig, ax = plt.subplots()

    ax.set(xlim=(0, int(max(x)*1.1)), ylim=(0, max(max(y),sad.capacity*1.2)))

    ax.errorbar(x, y,yerr=err,fmt=".-",linewidth=0.75)
    ax.set_title("fitness en fonction de la taille de la liste TABU")
    plt.show(block=True)

if __name__ == '__main__':
    main()
