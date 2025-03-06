#pour dev
from SadObject import *
import parser
from tabou_solver import Tabou_solver

import numpy
print(numpy.__path__)

import numpy as np
import matplotlib.pyplot as plt


sad = parser.loadFromFile("Data/pi-12-100-1000-001.kna")

fitnessList = []
rangeList = []
for i in range(100) :
    sad.reinit()
    
    solver = Tabou_solver(sad)
    solver.MAX_ITER = i*i//2
    solver.solve()
    
    fitnessList.append(sad.bestFitness)
    rangeList.append(solver.MAX_ITER)
    
fig, ax = plt.subplots()
ax.set(xlim=(0, max(rangeList)), ylim=(0, max(fitnessList)))

plt.ion()

(line,) = ax.plot([], [])  # initially an empty line

timestep = 0.1  # in seconds

for i in range(1, len(rangeList) + 1):
    line.set_data(rangeList[:i], fitnessList[:i])
    plt.pause(timestep)
plt.show(block=True)
