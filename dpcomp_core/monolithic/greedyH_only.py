from dpcomp_core.monolithic import estimate_engine
from dpcomp_core.monolithic.routine_engines import routine_engine
from dpcomp_core.mixins import Marshallable
from dpcomp_core.monolithic import greedyH
import numpy
from dpcomp_core import util

# running only with greedyH as estimate engine, no partition engine used
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
