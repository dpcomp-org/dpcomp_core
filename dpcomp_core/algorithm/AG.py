from __future__ import division
from __future__ import absolute_import
from builtins import range
import math
import numpy
from . import estimate_engine
from dpcomp_core import util

'''
Canonical name:     AGrid (2D)
Additional aliases: AG
Reference:          [W. Qardaji, W. Yang, and N. Li. Differentially private grids for geospatial data. ICDE, 2013.](http://dl.acm.org/citation.cfm?id=2510649.2511274)
Invocation:         dpcomp_core.algorithm.AG.AG_engine()
Implementation:     DPComp team
'''
class AG_engine(estimate_engine.estimate_engine):
    """ Estimate a 2D dataset by using adaptive grids. """
    
    def __init__(self, c = 10, c2 = 5, alpha = 0.5, short_name = 'AGrid'):
        # c,c2 are the constant parameter controling the number of cells in each level
        # alpha is the ratio of budget split on the first level
        self.init_params = util.init_params_from_locals(locals())

        self.c = c
        self.c2 = c2
        self.alpha = alpha
        self.short_name = short_name
    
    
    @staticmethod
    def GenerateCells(x,n,m,num1,num2,grid):
        # this function used to generate cells and compute their counts given the size
        cells = []
        counts = []
        for i in range(num1):
            for j in range(num2):
                lb = [i*grid,j*grid]
                rb = [(i+1)*grid-1,(j+1)*grid-1]
                if rb[0] >= n:
                    rb[0] = n-1
                if rb[1] >= m:
                    rb[1] = m-1
                
                cells = cells + [[lb,rb]]
                
                cnt = 0;
                for k in range(lb[0],rb[0]+1):
                    cnt = cnt + sum(x[k][lb[1]:rb[1]+1])
                counts = counts + [cnt]
        
        return cells,counts

    @staticmethod
    def CountPerturb(x,cells,counts,epsilon,alpha,c2,prng):
        # generate second level grids and compute the noisy counts
        n,m = x.shape
        y = numpy.ndarray((n,m),'float32')
        y.fill(0)
        
        noisycnt = counts + prng.laplace(0,util.old_div(1.0,(alpha * epsilon)),len(counts))
        
        #second level grids and compute noisy counts with postprocessings
        for k in range(len(cells)):
            x1,y1,x2,y2 = cells[k][0][0],cells[k][0][1],cells[k][1][0],cells[k][1][1]
            nn = x2-x1+1
            mm = y2-y1+1
            
            #compute second level grid size
            if noisycnt[k] <= 0:
                m2 = 1
            else:
                m2 = int(math.sqrt(noisycnt[k]*(1-alpha)*epsilon/c2)-1) + 1
            M2 = m2**2
            
            newgrid = int(math.sqrt(nn*mm*1.0/M2)-1) + 1
            if newgrid <= 0:
                newgrid = 1;
            num1 = int(util.old_div((nn-1), newgrid) + 1)
            num2 = int(util.old_div((mm-1), newgrid) + 1)
            
            curX = numpy.ndarray((nn,mm),'float32')
            for xx in range(x1,x2+1):
                curX[xx-x1] = x[xx][y1:y2+1]
            
            newcells,newcounts = AG_engine.GenerateCells(curX,nn,mm,num1,num2,newgrid)
            ncounts = newcounts + prng.laplace(0,util.old_div(1.0,((1-alpha)*epsilon)),len(newcounts))
            
            #postprocessing
            newncnt = (alpha*m2)**2 / ((1-alpha)**2 + (alpha*m2)**2) * noisycnt[k] + (1-alpha)**2 / ((1-alpha)**2 + (alpha*m2)**2) * sum(ncounts)
            
            for i in range(len(newcells)):
                upcnt = ncounts[i] + 1.0/len(newcells) * (newncnt - sum(ncounts))
                xx1,yy1,xx2,yy2 = x1 + newcells[i][0][0], y1 + newcells[i][0][1], x1 + newcells[i][1][0], y1 + newcells[i][1][1]
                upavg = upcnt*1.0 / ((xx2-xx1+1)*(yy2-yy1+1))
                
                for j in range(xx1,xx2+1):
                    y[j][yy1:yy2+1] = upavg

        return y

    def Run(self,Q,x,epsilon,seed):
        assert seed is not None, 'seed must be set'

        prng = numpy.random.RandomState(seed)

        assert len(x.shape)==2, '%s is defined for 2D data only' % self.__class__.__name__

        n,m = x.shape
        N = sum(sum(x))
        # compute number of cells in the first level
        m1 = int(util.old_div(math.sqrt(util.old_div((N*epsilon), self.c)), 4) - 1) + 1
        if m1 < 10:
            m1 = 10
        M = m1**2
        
        grid = int(math.sqrt(n*m*1.0/M)-1)+1
        if grid <= 0:
            grid = 1;
        
        num1 = int(util.old_div((n-1), grid) + 1)
        num2 = int(util.old_div((m-1), grid) + 1)
        
        cells,counts = AG_engine.GenerateCells(x,n,m,num1,num2,grid)
        
        y = AG_engine.CountPerturb(x,cells,counts,epsilon,self.alpha,self.c2,prng)
        
        return y

