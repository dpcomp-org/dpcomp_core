from __future__ import division
from __future__ import absolute_import
from .estimate_engine import estimate_engine
import numpy
from dpcomp_core import util

class uniform_engine(estimate_engine):
    """Estimate a dataset by assuming it is uniform over the domain; assuming total number of records is known."""

    def __init__(self):
        self.init_params = util.init_params_from_locals(locals())

    def Run(self, Q, x, epsilon, seed=None):
        return numpy.ones_like(x,dtype=numpy.float32) * x.sum() / x.size # assuming m is known

'''
Canonical name:     Uniform
Additional aliases: UniformNoisy
Reference:          -
Invocation:         dpcomp_core.algorithm.uniform.uniform_noisy_engine()
Implementation:     DPComp team
'''
class uniform_noisy_engine(estimate_engine):
    """Estimate a dataset by assuming it is uniform over the domain; total number of records derived privately according to epsilon."""

    def __init__(self,short_name = "Uniform"):
        self.init_params = util.init_params_from_locals(locals())
        self.short_name = short_name

    def Run(self, Q, x, epsilon, seed=None):
        # rewritten to support nd-array input x:
        assert seed is not None, 'seed must be set'

        prng = numpy.random.RandomState(seed)

        m = x.sum() + prng.laplace(0.0, util.old_div(1.0, epsilon), 1)
        return numpy.ones_like(x,dtype=numpy.float32) * m / x.size # assuming m is known
