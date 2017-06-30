from __future__ import division
from __future__ import absolute_import
from builtins import range
import numpy
from . import estimate_engine
from . import UG
from dpcomp_core import util

'''
Canonical name:     DPCube (2D)
Additional aliases: -
Reference:          [Y. Xiao, L. Xiong, L. Fan, S. Goryczka, and H. Li. DPCube: Differentially private histogram release through multidimensional partitioning. Transactions of Data Privacy, 2014.](http://dl.acm.org/citation.cfm?id=2870615)
Invocation:         dpcomp_core.algorithm.DPcube.DPcube_engine()
Implementation:     DPComp team
'''
class DPcube_engine(estimate_engine.estimate_engine):
    """ Estimate a 2D dataset by using dpcube method """

    def __init__(self, gz = 11, alpha = 0.5,short_name = 'DPCube'):
        # gz control the grid size for partition, alpha is the ratio of budget split for computing partition points
        self.init_params = util.init_params_from_locals(locals())
        self.gz = gz
        self.alpha = alpha
        self.short_name = short_name
    
    @staticmethod
    def bucketcost(X,l1,l2):
        # this function used to compute the intermediate costs of buckets
        
        p = []
        pp = []
        for i in range(l1+1):
            if i == 0:
                p = p + [numpy.zeros(l2+1)]
                pp = pp + [numpy.zeros(l2+1)]
                continue
            
            x1 = numpy.zeros(l2+1)
            x2 = numpy.zeros(l2+1)
            for j in range(l2):
                x1[j+1] = x1[j] + X[i-1][j]
                x2[j+1] = x2[j] + X[i-1][j]**2
            
            p = p + [x1]
            pp = pp + [x2]
        
        for i in range(l1):
            for j in range(l2+1):
                p[i+1][j] = p[i][j] + p[i+1][j]
                pp[i+1][j] = pp[i][j] + pp[i+1][j]
        
        return p,pp


    @staticmethod
    def Compute(p,pp,x0,y0,x1,y1):
        #this function used to compute the cost of bucket (x0,y0,x1,y1)
        a1 = pp[x1+1][y1+1] + pp[x0][y0] - pp[x0][y1+1] - pp[x1+1][y0]
        a2 = p[x1+1][y1+1] + p[x0][y0] - p[x0][y1+1] - p[x1+1][y0]
        
        return a1 - a2**2 * 1.0 / ((x1-x0+1)*(y1-y0+1))
    
    @staticmethod
    def dpcube(epsilon,p,pp,rp,X2,start,end,prng):
        # this function used to compute the noisy counts
        (x0,y0) = start
        (x1,y1) = end
        
        len0 = x1 - x0 + 1
        len1 = y1 - y0 + 1
        
        if len0 > len1:
            bias = DPcube_engine.Compute(p,pp,x0,y0,x1,y1)
            cur = bias + util.old_div(1.0,epsilon)
            flag = False
            pos = x0
            
            for k in range(x0,x1):
                bias1 = DPcube_engine.Compute(p,pp,x0,y0,k,y1)
                bias2 = DPcube_engine.Compute(p,pp,k+1,y0,x1,y1)
                
                if bias1 + bias2 + util.old_div(2.0, epsilon) < cur:
                    cur = bias1 + bias2 + util.old_div(2.0,epsilon)
                    flag = True
                    pos = k
        
            if flag == True:
                DPcube_engine.dpcube(epsilon,p,pp,rp,X2,(x0,y0),(pos,y1),prng)
                DPcube_engine.dpcube(epsilon,p,pp,rp,X2,(pos+1,y0),(x1,y1),prng)
            else:
                ncnt = rp[x1+1][y1+1] + rp[x0][y0] - rp[x0][y1+1] - rp[x1+1][y0] + prng.laplace(0.0,util.old_div(1.0,epsilon))
                navg = ncnt * 1.0 / (len0*len1)
                
                for i in range(x0,x1+1):
                    X2[i][y0:y1+1] = navg
                    
        else:
            bias = DPcube_engine.Compute(p,pp,x0,y0,x1,y1)
            cur = bias + util.old_div(1.0,epsilon)
            flag = False
            pos = y0
                    
            for k in range(y0,y1):
                bias1 = DPcube_engine.Compute(p,pp,x0,y0,x1,k)
                bias2 = DPcube_engine.Compute(p,pp,x0,k+1,x1,y1)
                                
                if bias1 + bias2 + util.old_div(2.0,epsilon) < cur:
                    cur = bias1 + bias2 + util.old_div(2.0,epsilon)
                    flag = True
                    pos = k
                                                
            if flag == True:
                DPcube_engine.dpcube(epsilon,p,pp,rp,X2,(x0,y0),(x1,pos),prng)
                DPcube_engine.dpcube(epsilon,p,pp,rp,X2,(x0,pos+1),(x1,y1),prng)
            else:
                ncnt = rp[x1+1][y1+1] + rp[x0][y0] - rp[x0][y1+1] - rp[x1+1][y0] + prng.laplace(0.0,util.old_div(1.0,epsilon))
                navg = ncnt * 1.0 / (len0*len1)
                                                                        
                for i in range(x0,x1+1):
                    X2[i][y0:y1+1] = navg
                    


    def Run(self,Q,x,epsilon,seed):

        assert seed is not None, 'seed must be set'

        prng = numpy.random.RandomState(seed)

        assert len(x.shape)==2, '%s is defined for 2D data only' % self.__class__.__name__

        l1,l2 = x.shape
        
        # use alpha*epsilon budget to generate synthetic dataset by UG
        X1 = UG.UG_engine(gz=self.gz).Run(Q,x,epsilon*self.alpha,seed)
        
        X2 = numpy.ndarray((l1,l2),'float32')
        X2.fill(0)
        
        
        rp,rpp = DPcube_engine.bucketcost(x,l1,l2)
        
        p,pp = DPcube_engine.bucketcost(X1,l1,l2)
        
        
        DPcube_engine.dpcube((1-self.alpha)*epsilon,p,pp,rp,X2,(0,0),(l1-1,l2-1),prng);
        
        return X2
