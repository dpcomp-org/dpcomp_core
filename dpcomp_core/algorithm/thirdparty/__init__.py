from __future__ import absolute_import
import math
from dpcomp_core import util
from dpcomp_core.algorithm import estimate_engine
import numpy
# import the wrapped mean strcture first code
from .xiaokui import structFirst

# import Acs12 lib
from .Acs12.lib import EFPA
from .Acs12.lib import Clustering
'''
Canonical name:     StructureFirst (1D)
Additional aliases: SF
Reference:          [J. Xu, Z. Zhang, X. Xiao, Y. Yang, G. Yu, and M. Winslett. Differentially private histogram publication. VLDB, 2013.](http://dl.acm.org/citation.cfm?id=2581852&CFID=877817809&CFTOKEN=72173205)
Invocation:         dpcomp_core.algorithm.thirdparty.StructureFirst_engine()
Implementation:     Authors of original paper
'''
class StructureFirst_engine(estimate_engine.estimate_engine):
    '''Estimate engine with the structure first algorithm.'''

    def __init__(self,short_name = "SF"):
        self.init_params = util.init_params_from_locals(locals())
        self.short_name = short_name

    @staticmethod
    def Run(Q, x, epsilon,seed):
        return numpy.array(structFirst.structureFirst(x, len(x), epsilon,seed))


'''
Canonical name:     EFPA (1D)
Additional aliases: -
Reference:          [G. Acs ,C .Castelluccia ,and R. Chen. Differentially private histogram publishing through lossy compression. ICDM, 2012.](http://ieeexplore.ieee.org/document/6413718/)
Invocation:         dpcomp_core.algorithm.thirdparty.efpa_engine()
Implementation:     Authors of original paper
'''
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


'''
Canonical name:     PHP (1D)
Additional aliases: -
Reference:          [G. Acs ,C .Castelluccia ,and R. Chen. Differentially private histogram publishing through lossy compression. ICDM, 2012.](http://ieeexplore.ieee.org/document/6413718/)
Invocation:         dpcomp_core.algorithm.thirdparty.php_engine()
Implementation:     Authors of original paper
'''
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
