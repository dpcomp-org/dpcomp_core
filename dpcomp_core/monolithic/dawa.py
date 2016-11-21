from dpcomp_core.monolithic import estimate_engine
from dpcomp_core.monolithic.partition_engines import l1partition
from dpcomp_core.monolithic.routine_engines import routine_engine
from dpcomp_core.mixins import Marshallable
from dpcomp_core.monolithic import greedyH
import numpy
from dpcomp_core import util

class dawa_engine(routine_engine.transform_engine_qtqmatrix, Marshallable):
    """ Estimate a 1D dataset by using adaptive grids. """

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
