import numpy
from dpcomp_core.monolithic import estimate_engine
from dpcomp_core import util

class identity_engine(estimate_engine.estimate_engine):
    """Estimate a dataset by asking each of its entry with laplace mechanism."""
    
    def __init__(self,short_name ='Identity'):
        self.init_params = util.init_params_from_locals(locals())
        self.short_name = short_name

    
    def Run(self, Q, x, epsilon, seed):
        assert seed is not None, 'seed must be set'

        prng = numpy.random.RandomState(seed)

        return x + prng.laplace(0.0, 1.0 / epsilon, x.shape)
