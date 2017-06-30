from __future__ import division
from __future__ import absolute_import
from builtins import range
import math
import numpy
from . import estimate_engine
from dpcomp_core import util

'''
Canonical name:     UGrid (2D)
Additional aliases: UG
Reference:          [W. Qardaji, W. Yang, and N. Li. Differentially private grids for geospatial data. ICDE, 2013.](http://dl.acm.org/citation.cfm?id=2510649.2511274)
Invocation:         dpcomp_core.algorithm.UG.UG_engine()
Implementation:     DPComp team
'''
class UG_engine(estimate_engine.estimate_engine):
    
    """ Estimate a 2D dataset by using uniform grids. """
    
    def __init__(self, c = 10,gz=0,short_name ="UGrid"):
        # c is the constant parameter controling the number of cells

        self.init_params = util.init_params_from_locals(locals())
        self.c = c
        self.gz= gz
        self.short_name = short_name
    
    @staticmethod
    def GenerateCells(n,m,num1,num2,grid):
        # this function used to generate all the cells
        cells = []
        for i in range(num1):
            for j in range(num2):
                lb = [int(i*grid),int(j*grid)]
                rb = [int((i+1)*grid-1),int((j+1)*grid-1)]
                if rb[0] >= n:
                    rb[0] = int(n-1)
                if rb[1] >= m:
                    rb[1] = int(m-1)
                
                cells = cells + [[lb,rb]]
        
        return cells

    @staticmethod
    def CountPerturb(x,cells,epsilon,prng):
        # this function used to perturb counts based on generated grids
        n,m = x.shape
        y = numpy.ndarray((n,m),'float32')
        y.fill(0)
        
        for cell in cells:
            x1,y1,x2,y2 = int(cell[0][0]),int(cell[0][1]),int(cell[1][0]),int(cell[1][1])
            cnt = 0
            for i in range(x1,x2+1):
                cnt = cnt + sum(x[i][y1:y2+1])
        
            navg = util.old_div((prng.laplace(cnt,util.old_div(1.0,epsilon))), ((x2-x1+1)*(y2-y1+1)))
        
            for i in range(x1,x2+1):
                y[i][y1:y2+1] = navg

        return y
    
    def Run(self,Q,x,epsilon,seed):
        
        assert seed is not None, 'seed must be set'
        prng = numpy.random.RandomState(seed)
        
        assert len(x.shape)==2, '%s is defined for 2D data only' % self.__class__.__name__

        n,m = x.shape
        # assume the data scale is non private information. 
        N = x.sum()
        # compute number of cells
        M = util.old_div((N*epsilon), self.c)
        
        if self.gz == 0:
            grid = int(math.sqrt(n*m/M)-1)+1
        else:
            grid = int(self.gz)
        
        if grid < 1:
            grid = 1
        
        num1 = int(util.old_div((n-1), grid) + 1)
        num2 = int(util.old_div((m-1), grid) + 1)
        
        cells = UG_engine.GenerateCells(n,m,num1,num2,grid)
        
        y = UG_engine.CountPerturb(x,cells,epsilon,prng)
        
        return y

