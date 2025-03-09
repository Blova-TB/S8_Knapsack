#pour dev
from testor import *
from SadObject import *
import parser
import tabou_solver as tbs
from MyIterator import *

import numpy as np
import matplotlib.pyplot as plt
import math

def show_plot(x,y,err,title,block=True) :
    plt.cla()
    plt.title(title)
    plt.errorbar(x, y,yerr=err,fmt=".",linewidth=0.75)
    plt.autoscale()
    plt.show(block=block)

def increment(i) :
    return i+50

def main():
    sad = parser.loadFromFile("Data/pi-12-10000-1000-001.kna")
    test = Testor(tbs.Tabou_solver(sad,tabu_size=200))

    #iterator = MyIterator(1, 800, increment)
    iterator = range(1,10,3)
    
    (x,y,err) = test.test(iterator,tbs.reinit_iter_changer,1)
    
    title = "fitness en fonction de la taille de la liste TABU"

    
    np.set_printoptions(legacy='1.25')
    print("index:",x)
    print("values:",y)
    print("variance:",err)
    
    show_plot(x, y, err, title, block=True)

if __name__ == '__main__':
    main()
