from __future__ import division
from __future__ import absolute_import
from builtins import range
import math
import numpy
from . import estimate_engine
from . import UG
from dpcomp_core import util


'''
Canonical name:     DPCube (1D)
Additional aliases: -
Reference:          [Y. Xiao, L. Xiong, L. Fan, S. Goryczka, and H. Li. DPCube: Differentially private histogram release through multidimensional partitioning. Transactions of Data Privacy, 2014.](http://dl.acm.org/citation.cfm?id=2870615)
Invocation:         dpcomp_core.algorithm.DPcube1D.DPcube1D_engine()
Implementation:     DPComp team
'''
class DPcube1D_engine(estimate_engine.estimate_engine):
    """ Estimate a 2D dataset by using dpcube method """

    def __init__(self, gz = 11, alpha = 0.5,short_name = "DPCube"):
        # gz control the grid size for partition, alpha is the ratio of budget split for computing partition points
        self.init_params = util.init_params_from_locals(locals())

        self.gz = gz
        self.alpha = alpha
        self.short_name = short_name
    
    @staticmethod
    def bucketcost(X,l):
        # this function used to compute the intermediate costs of buckets
        
        p = numpy.zeros(l+1)
        pp = numpy.zeros(l+1)
        for i in range(l):
            p[i+1] = p[i] + X[i]
            pp[i+1] = pp[i] + X[i]**2           

        return p,pp


    @staticmethod
    def Compute(p,pp,left,right):
        #this function used to compute the cost of bucket (left,right)
        a1 = pp[right+1] - pp[left]
        a2 = p[right+1] - p[left]
        
        return a1 - a2**2 * 1.0 / (right - left + 1)
    
    @staticmethod
    def dpcube(epsilon,p,pp,rp,X2,left,right,prng):
        # this function used to compute the noisy counts
       
        len = right - left + 1 
        bias = DPcube1D_engine.Compute(p,pp,left,right)
        cur = bias + util.old_div(1.0,epsilon)
        flag = False
        pos = left
            
        for k in range(left,right):
            bias1 = DPcube1D_engine.Compute(p,pp,left,k)
            bias2 = DPcube1D_engine.Compute(p,pp,k+1,right)
            if bias1 + bias2 + util.old_div(2.0, epsilon) < cur:
                cur = bias1 + bias2 + util.old_div(2.0,epsilon)
                flag = True
                pos = k
        
        if flag == True:
            DPcube1D_engine.dpcube(epsilon,p,pp,rp,X2,left,pos,prng)
            DPcube1D_engine.dpcube(epsilon,p,pp,rp,X2,pos+1,right,prng)
        else:
            ncnt = rp[right+1] - rp[left] + prng.laplace(0.0,util.old_div(1.0,epsilon))
            navg = ncnt * 1.0 / len
                
            for i in range(left,right+1):
                X2[i] = navg
                    
    @staticmethod                
    def GetsynData(x,gz,epsilon,prng):
        l = len(x)
        y = numpy.zeros(l)
        
        p = util.old_div(l,gz)
        for i in range(p):
            nc = sum(x[i*gz:(i+1)*gz]) 
            nc = nc + prng.laplace(0.0,util.old_div(1.0,epsilon))
            for j in range(gz):
                y[i*gz+j] = nc*1.0/gz   

        if l % gz != 0:
            nc = sum(x[p*gz:])
            nc = nc + prng.laplace(0.0,util.old_div(1.0,epsilon))
            for j in range(l - p*gz):
                y[p*gz+j] = nc*1.0/(l-p*gz) 
        return y

    def Run(self,Q,x,epsilon,seed):

        assert seed is not None, 'seed must be set'
        prng = numpy.random.RandomState(seed)

        assert len(x.shape)==1, '%s is defined for 1D data only' % self.__class__.__name__

        l = len(x)
        
        # use alpha*epsilon budget to generate synthetic dataset by using grid size gz
        X1 = DPcube1D_engine.GetsynData(x,self.gz,self.alpha*epsilon,prng)
      
        X2 = numpy.zeros(l)
        rp,rpp = DPcube1D_engine.bucketcost(x,l)
        p,pp = DPcube1D_engine.bucketcost(X1,l)
        DPcube1D_engine.dpcube((1-self.alpha)*epsilon,p,pp,rp,X2,0,l-1,prng);
        return X2
