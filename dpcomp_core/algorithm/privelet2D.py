from __future__ import division
from __future__ import absolute_import
from builtins import range
import math
import numpy
from . import estimate_engine
from dpcomp_core import util

'''
Canonical name:     Privelet (2D)
Additional aliases: -
Reference:          [ X. Xiao, G. Wang, and J. Gehrke. Differential privacy via wavelet transforms. ICDE, 2010.](http://dl.acm.org/citation.cfm?id=2007020)
invocation:         dpcomp_core.algorithm.privelet2D.privelet2D_engine()
Implementation:     DPComp team
'''
class privelet2D_engine(estimate_engine.estimate_engine):
    """ Estimate a 2D dataset by using wavelet transformation """
    
    def __init__(self,short_name = "Privelet"):
        self.init_params = util.init_params_from_locals(locals())
        self.short_name = short_name

    @staticmethod
    def _wave(t,m):
        y = numpy.array(t)
        n = len(t)
        for c in range(m):
            y[:n] = numpy.hstack([y[:n][0::2] + y[:n][1::2],y[:n][0::2]-y[:n][1::2]])
            n = util.old_div(n, 2)
        
        return y
    
    @staticmethod
    def _dewave(t,m):
        y = numpy.array(t)
        n = 2
        half_n = 1
        for c in range(m):
            y[:n:2],y[1:n:2] = util.old_div((y[:half_n] + y[half_n:n]),2.0) , util.old_div((y[:half_n] - y[half_n:n]),2.0)
            n = n * 2
            half_n = half_n * 2
        
        return y
    
    
    @staticmethod
    def Run(Q, x, epsilon,seed):

        assert seed is not None, 'seed must be set'
        prng = numpy.random.RandomState(seed)

        assert len(x.shape)==2, '%s is defined for 2D data only' % self.__class__.__name__

        l1,l2 = x.shape
        
        m1 = int(math.ceil(math.log(l1,2)))
        m2 = int(math.ceil(math.log(l2,2)))
        
        
        #encode process
        X1 = []
        for i in range(2**m1):
            t = numpy.zeros(2**m2);
            if i < l1:
                t[:l2] = x[i]
            X1 = X1 + [t]
        
        Y = []
        for i in range(2**m1):
            t = X1[i]
            y = privelet2D_engine._wave(t,m2)
            Y = Y + [y]
        
        for i in range(2**m2):
            t = numpy.zeros(2**m1)
            for j in range(2**m1):
                t[j] = Y[j][i]
            y = privelet2D_engine._wave(t,m1)
            for j in range(2**m1):
                Y[j][i] = y[j]
    
        #add Laplace noise
        for i in range(2**m1):
            Y[i] = Y[i] + prng.laplace(0,(m1+1.0)*(m2+1.0)/epsilon, 2**m2)

        #decode process
        for i in range(2**m2):
            t = numpy.zeros(2**m1)
            for j in range(2**m1):
                t[j] = Y[j][i]
            y = privelet2D_engine._dewave(t,m1)
            for j in range(2**m1):
                Y[j][i] = y[j]

        X1 = []
        for i in range(2**m1):
            t = Y[i]
            y = privelet2D_engine._dewave(t,m2)
            X1 = X1 + [y]

        est = numpy.ndarray((l1,l2),'float')
        for i in range(l1):
            est[i] = X1[i][:l2]

        return est
