import math
from dpcomp_core import util
from dpcomp_core.monolithic import estimate_engine
import numpy
# import the wrapped mean strcture first code
from xiaokui import structFirst

# import Acs12 lib
from Acs12.lib import EFPA
from Acs12.lib import Clustering

class StructureFirst_engine(estimate_engine.estimate_engine):
    '''Estimate engine with the structure first algorithm.'''

    def __init__(self,short_name = "SF"):
        self.init_params = util.init_params_from_locals(locals())
        self.short_name = short_name

    @staticmethod
    def Run(Q, x, epsilon,seed):
        return numpy.array(structFirst.structureFirst(x, len(x), epsilon,seed))



class efpa_engine(estimate_engine.estimate_engine):
    '''Estimate engine with the EFPA algorithm.'''
    def __init__(self,short_name = "EFPA"):
        self.init_params = util.init_params_from_locals(locals())
        self.short_name = short_name
    @staticmethod
    def Run(Q, x, epsilon,seed):

        assert seed is not None, 'seed must be set'
        prng = numpy.random.RandomState(seed)
        return numpy.array(EFPA.EFPA(x, 1, epsilon,prng))



class php_engine(estimate_engine.estimate_engine):
    '''Estimate engine with P-HP algorithm.'''#
    def __init__(self,short_name ="PHP"):
        self.init_params = util.init_params_from_locals(locals())
        self.short_name = short_name
    @staticmethod
    def Run(Q, x, epsilon,seed):

        assert seed is not None, 'seed must be set'
        prng = numpy.random.RandomState(seed)
        
        return numpy.array(Clustering.Clustering(epsilon*0.5, epsilon*0.5, 1,
                                     int(math.log(len(x),2)), 2000).run(x,prng))