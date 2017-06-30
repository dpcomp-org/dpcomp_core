"""Classes of MWEM engines. mwemND_engine is the MWEM we are using, works for 1 and 1+ dimension. Also the adaptive version. """
from __future__ import division
from __future__ import absolute_import
from builtins import range
import math
import numpy
import logging
from . import estimate_engine
from dpcomp_core import util


class mwemND_simple_engine(estimate_engine.estimate_engine):
    """Basic Multiplictive weight mechanism engine."""

    def __init__(self, nrounds = 10, ratio = 0.5):
        """Set up basic parameters for MWEM.
        
        nrounds(10) - how many rounds are MWEM run.
        ratio(0.5) - the ratio of privacy budget used for query selection.
        """
        self._nrounds = nrounds
        self._ratio = ratio
        if ratio <= 0 or ratio >= 1:
            raise ValueError('ratio must in range (0, 1)')

    
    def Run(self, Q, x, epsilon, seed):
        assert seed is not None, 'seed must be set'

        prng = numpy.random.RandomState(seed)
        Q1=list(Q.query_list)# leave Q as it is for future evaluation 

        # here we assume the total count is known
        # create uniform estimate based on total count
        hatx = numpy.empty_like(x)
        hatx.fill( util.old_div(x.sum(), float(x.size)) )

        selepsilon = epsilon * self._ratio
        queryepsilon = epsilon - selepsilon
        
        assert(self._nrounds <= len(Q1)) # the maximum possible number of rounds is the size of Q. 
        # selected queries will be removed from Q, added to list of estimated queries
        estQ = []
        nrounds = self._nrounds
        for c in range(nrounds):
            i = self._exponentialMechanism(x, hatx, Q1, util.old_div(selepsilon, nrounds) ,prng)   # get index of selected query
            q = Q1[i]
            del Q1[i]    # no longer a candidate in next round
            sens=q.sens()
            est = q.eval(x) + prng.laplace(0.0, sens * nrounds / queryepsilon, 1)
            estQ.append( (q,est) )
            hatx = self._update(hatx, q, est)   # update using only current q and estimate

        return hatx


    @staticmethod   
    def _exponentialMechanism(x, hatx, Q, epsilon,prng):
        """Choose the worst estimated query (set) using the exponential mechanism.

        x - true data vector
        hatx - estimated data vector
        Q - the queries to be chosen from
        epsilon - private parameter
        """
        diffx = x - hatx
        # compute the error of each query 
        error = numpy.array([abs(q.eval(diffx)) for q in Q])    # evaluate range queries on difference vector

        # compute the sampling probability
        merr = max(error)

        logging.debug('  EXP-MECH: epsilon  %f' % epsilon )  
        logging.debug('  EXP-MECH: OPTIMAL index %s / error %f / query %s' % (error.argmax(), merr, Q[error.argmax()]) )
        
        prob = numpy.exp( epsilon* (error - merr) / 2.0 )

        logging.debug('  EXP-MECH: prob sum %f / prob %s' % (sum(prob), sorted(prob,reverse=True)[0:5]))

        sample = prng.random_sample() * sum(prob)
        for c in range(len(prob)):
            sample -= prob[c]
            if sample <= 0:
                logging.debug('  EXP-MECH: CHOSEN index %s / error %f / query %s' % (c, error[c], Q[c]) )
                return c
        
        logging.debug('  EXP-MECH: CHOSEN index %s / error %f / query %s' % (len(prob)-1, error[len(prob)-1], Q[len(prob)-1]) )
        return len(prob)-1

    @staticmethod
    def _update(hatx, q, est):
        """basic multiplicative weight update.
        update one single query, one round"""
        total = hatx.sum()
        error = est - q.eval(hatx) # difference between query ans on current estimated data and the observed answer 

        q1 = q.asArray(hatx.shape) # transform a query object into a nd array
        
        hatx = hatx * numpy.exp( q1 * error / (2.0 * total) )
        hatx *= util.old_div(total, hatx.sum())     
        return hatx

'''
Canonical name:     MWEM (ND)
Additional aliases: -
Reference:          [M. Hardt, K. Ligett, and F. McSherry. A simple and practical algorithm for differentially private data release. NIPS, 2012.](http://dl.acm.org/citation.cfm?id=2999325.2999396)
Invocation:         dpcomp_core.algorithm.mwemND.mwemND_engine()
Implementation:     DPComp team
'''
class mwemND_engine(mwemND_simple_engine):
    """MWEM engine with Frank's enhanced update method."""

    def __init__(self, nrounds = 10, ratio = 0.5, updateround = 100,short_name ='MWEM'):
        """Set up parameters for MWEM.

        nrounds(10) - how many rounds are MWEM run.
        ratio(0.5) - the ratio of privacy budget used for query selection.
        updateround(100) - the number of iterations in each update.
        """
        self.init_params = util.init_params_from_locals(locals())
        
        self._updateround = updateround
        super(type(self), self).__init__(nrounds, ratio)
        self.short_name = short_name


    def _updateH(self, hatx, estlist):
        """Update using all historical results for multiple rounds"""
        total = hatx.sum()
        for c in range(self._updateround):
            for q, est in estlist:
                hatx = mwemND_simple_engine._update(hatx,q,est)
        return hatx

    def Run(self, Q, x, epsilon, seed):
        assert seed is not None, 'seed must be set'

        prng = numpy.random.RandomState(seed)

        # here we assume the total count is known
        # create uniform estimate based on total count
        hatx = numpy.empty_like(x,dtype='float64')
        #Note x is a histogram, type int. hatx is distribution, type float
        hatx.fill( util.old_div(x.sum(), float(x.size)) )

        Q1=list(Q.query_list)# leave Q as it is for future evaluation 

        selepsilon = epsilon * self._ratio
        queryepsilon = epsilon - selepsilon
        
        assert(self._nrounds <= len(Q1)) # the maximum possible number of rounds is the size of Q. 
        # selected queries will be removed from Q, added to list of estimated queries
        estQ = []
        nrounds = self._nrounds
        for c in range(nrounds):
            i = self._exponentialMechanism(x, hatx, Q1, util.old_div(selepsilon, nrounds) ,prng)  # get index of selected query
            q = Q1[i]

            sens=q.sens()

            est = q.eval(x) + prng.laplace(0.0, sens * nrounds / queryepsilon, 1)
            estQ.append( (q,est) )

            hatx = self._updateH(hatx, estQ)    # update using history 

            del Q1[i]   # no longer a candidate in next round


        return hatx

'''
Canonical name:     MWEM* (ND)
Additional aliases: MWEM_ADP
Reference:          -
Invocation:         dpcomp_core.algorithm.mwemND.mwemND_adaptive_engine()
Implementation:     DPComp team
'''
class mwemND_adaptive_engine(estimate_engine.estimate_engine):
    """Adaptive MWEM engine"""

    def __init__(self, index = 'DEFAULT1D',ratio = 0.5, updateround = 100, short_name = 'MWEM*'):
        self.init_params = util.init_params_from_locals(locals())

        self._vSEP = Lfunction[index][0]
        self._vRound = Lfunction[index][1]
        self._updateround = updateround
        self._ratio = ratio
        self.short_name = short_name
    
    def Run(self, Q, x, epsilon, seed):

        assert seed is not None, 'seed must be set'
        
        Ntotal = x.sum() 

        SEP =  Ntotal * epsilon
        self._nrounds = int(numpy.interp(SEP,self._vSEP ,self._vRound))

        engine = mwemND_engine(self._nrounds, self._ratio,self._updateround)
    
        hatx = engine.Run(Q, x, epsilon, seed)   
        
        return hatx

Lfunction ={ \
            #1D
            #POWER
            'DEFALUT1D':([0,1,10,100,1000,10000,100000,1000000,10000000,100000000,1000000000,1e+20],
                [2, 2, 2, 4, 8, 12, 60, 80, 140, 140, 140, 140]),
            #2D
            #TDNORMAL1
            'DEFALUT2D':([0,500.0,1000.0,5000.0,10000.0,100000.0,500000.0,1000000.0,5000000.0,10000000.0,100000000.0,1e+20],
                        [12,   12,    12,    32,     32,      60,     120,      140,      140,        140, 140, 140])
        
}


