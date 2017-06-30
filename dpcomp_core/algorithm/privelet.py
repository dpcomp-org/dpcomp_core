from __future__ import division
from __future__ import absolute_import
from builtins import range
import numpy
from . import estimate_engine
import math
from dpcomp_core import util
'''
Canonical name:     Privelet (1D)
Additional aliases: -
Reference:          [ X. Xiao, G. Wang, and J. Gehrke. Differential privacy via wavelet transforms. ICDE, 2010.](http://dl.acm.org/citation.cfm?id=2007020)
Invocation:         dpcomp_core.algorithm.privelet.privelet_engine()
Implementation:     DPComp team
'''
class privelet_engine(estimate_engine.estimate_engine):
    """Estimate a dataset by asking its wavelet parameters."""

    def __init__(self,short_name ="Privelet"):
        self.init_params = util.init_params_from_locals(locals())
        self.short_name = short_name

        
    @staticmethod
    def _wave(x, m):
        """Compute the wavelet parameters of dataset x with
        size 2^m.
        """
        y = numpy.array(x)
        n = len(x)
        for c in range(m):
            y[:n] = numpy.hstack([y[:n][0::2] + y[:n][1::2],
                                  y[:n][0::2] - y[:n][1::2]])
            n /= 2
        return y

    @staticmethod
    def _dewave(y, m):
        """Compute the original dataset from a set of wavelet parameters
        y with size 2^m.
        """
        x = numpy.array(y)
        n = 2
        half_n = 1
        for c in range(m):
            x[:n:2], x[1:n:2] = util.old_div((x[:half_n] + x[half_n:n]),2.0), \
                                util.old_div((x[:half_n] - x[half_n:n]),2.0)
            n *= 2
            half_n *= 2

        return x


    def Run(self,Q, x, epsilon, seed):

        assert seed is not None, 'seed must be set'
        prng = numpy.random.RandomState(seed)
        
        assert len(x.shape)==1, '%s is defined for 1D data only' % self.__class__.__name__

        n = len(x)
        if n <= 16:
            # don't convert to wavelet parameters for small domains
            return x + prng.laplace(0.0, util.old_div(1.0, epsilon), len(x))
        else:
            m = int(math.ceil(math.log(n, 2)))
            x1 = numpy.zeros(2**m)
            x1[:n] = x
            y1 = privelet_engine._wave(x1, m) + \
                 prng.laplace(0.0, util.old_div((m+1.0), epsilon), len(x1))

            return privelet_engine._dewave(y1, m)[:n]
