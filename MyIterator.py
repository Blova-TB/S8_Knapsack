from typing import Callable
import time

class MyIterator:
    def __init__(self,start :int, stop:int, incrementFunction:Callable[[int], int]) :
        self._start = start
        self._stop = stop
        self.incr = incrementFunction
        self._len =0
        
        timeout = time.time() + 1 #seconde de calcul max
        while( start < stop and time.time() < timeout):
            start = incrementFunction(start)
            self._len +=1
            
    
    def __iter__(self):
        self.i = self._start
        return self

    def __next__(self):
        if (self.i >= self._stop) :
            raise StopIteration
        x = self.i
        self.i = self.incr(self.i)
        return x
    
    def __len__(self):
        return self._len