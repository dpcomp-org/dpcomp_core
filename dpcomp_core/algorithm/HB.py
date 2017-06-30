from __future__ import division
from __future__ import absolute_import
from builtins import range
from . import h_tree
import math
import numpy as np
from dpcomp_core import util 
from . import estimate_engine


'''
Canonical name:     HB (1D)
Additional aliases: -
Reference:          [W. Qardaji, W. Yang,and N. Li. Understanding hierarchical methods for differentially private histograms. PVLDB, 2013.](http://dl.acm.org/citation.cfm?id=2556576)
Invocation:         dpcomp_core.algorithm.HB.HB_engine()
Implementation:     DPComp team
'''
class HB_engine(estimate_engine.estimate_engine):
    '''
    Use hierarchical strategy from Hay PVLDB 2010 using 
    branching from Qardaji PVLDB 2013.
    '''
    def __init__(self, short_name = "HB"):
        self.init_params = util.init_params_from_locals(locals())
        self.short_name = short_name

    def Run(self, Q, x, epsilon, seed):
        assert seed is not None, 'seed must be set'

        prng = np.random.RandomState(seed)

        assert len(x.shape)==1, '%s is defined for 1D data only' % self.__class__.__name__

        N = len(x)
        b = find_best_branching(N)
        return np.array(build_tree(x, epsilon,prng, b))

'''
Canonical name:     H (1D)
Additional aliases: Hierarchical
Reference:          [M. Hay,V. Rastogi,G. Miklau,and D. Suciu. Boosting the accuracy of differentially private histograms through consistency. PVLDB, 2010.](http://dl.acm.org/citation.cfm?id=1920970)
Invocation:         dpcomp_core.algorithm.HB.H2_engine()
Implementation:     DPComp team
'''
class H2_engine(estimate_engine.estimate_engine):
    '''
    Use hierarchical strategy from Hay PVLDB 2010 using 
    branching factor of 2.
    '''

    def __init__(self,short_name="hierarchical_complete"):
        self.init_params = util.init_params_from_locals(locals())
        self.short_name = short_name

    
    def Run(self, Q, x, epsilon, seed):
        assert seed is not None, 'seed must be set'

        prng = np.random.RandomState(seed)

        return np.array(build_tree(x, epsilon,prng))


'''
Technique from Qardaji et al. PVLDB 2013.
'''

def find_best_branching(N):
    '''
    Try all branchings from 2 to N and pick one 
    with minimum variance.
    '''
    min_v = float('inf')
    min_b = None
    for b in range(2,N+1):
        v = variance(N, b)
        if v < min_v:
            min_v = v
            min_b = b
    return min_b

def variance(N, b):
    '''Computes variance given domain of size N 
    and branchng factor b.  Equation 3 from paper.'''
    h = math.ceil(math.log(N, b))
    return ( ((b - 1) * h**3) - (util.old_div((2 * (b+1) * h**2), 3)))

def build_tree(x, epsilon,prng, b=2):

    # tree code requires len(x) be a power of b
    # if it is not, then pad x with 0s and then remove at end
    n = len(x)
    target_n = b**int(math.ceil(math.log(n, b)))
    if n < target_n:
        x = np.append(x, [0]*(target_n - n))
    H = h_tree.HTree(b, x)

    # add noise
    epsilon = util.old_div(float(epsilon), H.height)  # uniform allocation
    for node in H.postorder_iter():
        node.noisy = node.count + prng.laplace(0, util.old_div(1,epsilon))
    
    est_x = H.inference()
    return est_x[:n]  # truncate any padded zeros



