from __future__ import division
from __future__ import absolute_import
from builtins import range
from dpcomp_core.algorithm import estimate_engine
from .partition_engines import l1partition
from .routine_engines import routine_engine
from dpcomp_core.mixins import Marshallable
from dpcomp_core import util
from . import greedyH
import numpy
import math

'''
Canonical name:     DAWA (1D)
Additional aliases: -
Reference:          [C. Li, M. Hay, and G. Miklau. A data- and workload-aware algorithm for range queries under differential privacy. PVLDB, 2014.](http://dl.acm.org/citation.cfm?id=2732271) 
Invocation:         dpcomp_core.algorithm.dawa.dawa_engine()
Implementation:     DPComp team
'''
class dawa_engine(routine_engine.transform_engine_qtqmatrix, Marshallable):
    """ Estimate a 1D dataset using DAWA - L1partition followed by greedyH """

    def __init__(self, ratio = 0.5, max_block_size = None, short_name = "DAWA"):
        """ c,c2 are the constant parameter controlling the number of cells in each level
         alpha is the ratio of budget split on the first level beside total budget"""
        self.init_params = util.init_params_from_locals(locals())

        self._ratio = ratio 
        self._max_block_size = max_block_size
        self._partition_engine = l1partition.l1partition_approx_engine()
 
        self._estimate_engine = greedyH.greedyH_engine()
        self.short_name = short_name


    def Run(self, Q, x, epsilon, seed):

        assert seed is not None, 'seed must be set'

        return super(type(self),self).Run(Q, x, epsilon, seed)

'''
Canonical name:     DAWA (2D)
Additional aliases: -
Reference:          [C. Li, M. Hay, and G. Miklau. A data- and workload-aware algorithm for range queries under differential privacy. PVLDB, 2014.](http://dl.acm.org/citation.cfm?id=2732271) 
Invocation:         dpcomp_core.algorithm.dawa.dawa2D_engine()
Implementation:     DPComp team
'''
class dawa2D_engine(routine_engine.transform_engine_qtqmatrix_linear, Marshallable):
    """Estimate a 2D dataset by using DAWA on a 1d transform of 2d. """

    def __init__(self, ratio = 0.25,short_name = 'DAWA' ):
        # set ratio to 0 if no partition needed => GREEDYH_LINEAR,else DAWA_LINEAR.
        self.init_params = util.init_params_from_locals(locals())

        self._ratio = ratio
        self._partition_engine = l1partition.l1partition_approx_engine()
        self._estimate_engine = greedyH.greedyH_engine()
        self.short_name = short_name

    def Run(self, Q, x, epsilon, seed):

        assert seed is not None, 'seed must be set'
        assert len(x.shape)==2, '%s is defined for 2D data only' % self.__class__.__name__
        n1, n2 = x.shape
        Q = list(Q.query_list)

        # STEP 1: apply hilbert curve to get 1D
        # ... first expand x to be square and a power of 2
        d = 2**int(math.ceil(math.log(max(n1, n2), 2)))
        tmp = numpy.zeros([d, d], dtype='int32')
        tmp[:n1, :n2] = x  # embed input x into possibly bigger d x d array
        x = tmp  # x is now d x d square where d is a power of 2

        # ... now apply hilbert transform
        xcoords, ycoords = hilbert(d)  # coordinates of points along Hilbert curve on d x d square
        x1d = x[xcoords, ycoords]      # index into x at these points to get 1d representation

        # STEP 2: similarly transform queries
        m = len(Q)
        Qmat = numpy.zeros([m, len(x1d)])  # workload matrix: m by n, for m queries over 1d domain of size n
        for i in range(m):
            query = Q[i]
            query2d = query.asArray([d,d])    # query as d x d array
            query1d = query2d[xcoords, ycoords]  # array transformed to 1d via hilbert transform
            Qmat[i, :] = query1d  # embed this query into ith row of workload matrix

        # STEP 3: call DAWA_LINEAR
        if self._ratio == 0:
            self._partition_engine = None

       
        hatx1d = super(type(self),self).Run(Qmat,x1d, epsilon, seed)


        # STEP 4: invert hilbert curve transform to get 2D
        hatx2d = numpy.zeros([d, d], dtype='int32')
        hatx2d[xcoords, ycoords] = hatx1d  # assign the values of hatx1d into hatx2d at indexes (xcoords, ycoords)
        hatx2d = hatx2d[:n1, :n2] # remove excess: extract out the n1 x n2 portion of hatx2d

        return hatx2d

# running only with greedyH as estimate engine, no partition engine used
'''
Canonical name:     Greedy H (1D)
Additional aliases: greedyH
Reference:          [C. Li, M. Hay, and G. Miklau. A data- and workload-aware algorithm for range queries under differential privacy. PVLDB, 2014.](http://dl.acm.org/citation.cfm?id=2732271) 
Invocation:         dpcomp_core.algorithm.dawa.greedyH_only_engine()
Implementation:     DPComp team
'''
class greedyH_only_engine(routine_engine.transform_engine_qtqmatrix, Marshallable):
    """ Estimate a 2D dataset by using adaptive grids. """

    def __init__(self,short_name = "GreedyH"):
        
        self.init_params = util.init_params_from_locals(locals())
        self._max_block_size = None
        self._partition_engine = None
        self._estimate_engine = greedyH.greedyH_engine()
        self.short_name = short_name


    def Run(self, Q, x, epsilon, seed):

        assert seed is not None, 'seed must be set'

        return super(type(self),self).Run(Q, x, epsilon, seed)

def hilbert(N):
    """
    Produce coordinates of an NxN Hilbert curve.

    @param N:
         the length of side, assumed to be a power of 2 ( >= 2)

    @returns:
          x and y, each as an array of integers representing coordinates
          of points along the Hilbert curve. Calling plot(x, y)
          will plot the Hilbert curve.

    From Wikipedia
    """
    assert 2**int(math.ceil(math.log(N, 2))) == N, "N={0} is not a power of 2!".format(N)
    if N==2:
        return  numpy.array((0, 0, 1, 1)), numpy.array((0, 1, 1, 0))
    else:
        x, y = hilbert(util.old_div(N,2))
        xl = numpy.r_[y, x,     util.old_div(N,2)+x, N-1-y  ]
        yl = numpy.r_[x, util.old_div(N,2)+y, util.old_div(N,2)+y, util.old_div(N,2)-1-x]
        return xl, yl

