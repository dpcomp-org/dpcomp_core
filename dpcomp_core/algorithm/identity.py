from __future__ import division
from __future__ import absolute_import
import numpy
from . import estimate_engine
from dpcomp_core import util

'''
Canonical name:     Identity (ND)
Additional aliases: -
Reference:          [C. Dwork, F. McSherry, K. Nissim, and A. Smith. Calibrating noise to sensitivity in private data analysis. TCC, 2006.](http://dl.acm.org/citation.cfm?id=2180305)
Invocation:         dpcomp_core.monolithic.identity.identity_engine()
Implementation:     DPComp team
'''
class identity_engine(estimate_engine.estimate_engine):
    """Estimate a dataset by asking each of its entry with laplace mechanism."""
    
    def __init__(self,short_name ='Identity'):
        self.init_params = util.init_params_from_locals(locals())
        self.short_name = short_name

    
    def Run(self, Q, x, epsilon, seed):
        assert seed is not None, 'seed must be set'

        prng = numpy.random.RandomState(seed)

        return x + prng.laplace(0.0, util.old_div(1.0, epsilon), x.shape)
