import math
import numpy as np
from dpcomp_core.monolithic import estimate_engine
from dpcomp_core import util 

# AHP algorithm from
# "Towards Accurate Histogram Publication under Differential Privacy"
# Zhang, Chen, Xu, Meng, Xie
# SDM 2014


class ahp_engine(estimate_engine.estimate_engine):
    """Estimate a dataset by assuming it is uniform over the domain; total number of records derived privately according to epsilon."""

    def __init__(self, ratio = 0.85, eta = 0.35, short_name = 'AHP' ):
        self.init_params = util.init_params_from_locals(locals())
        self._ratio = ratio
        self._eta = eta
        self.short_name = short_name

    def Run(self, Q, x, epsilon, seed):
        assert seed is not None, 'seed must be set'

        prng = np.random.RandomState(seed)

        assert len(x.shape)==1, '%s is defined for 1D data only' % self.__class__.__name__
        return ahpr(x, epsilon, self._ratio, self._eta, prng)

class ahp_engine_adaptive(estimate_engine.estimate_engine):
        """Adaptive version that choose free parameters according to the product of epsilon and data scale."""
        
        def __init__(self, index = 'DEFAULT',totalBudget = 0.05, short_name = 'AHP_ADP' ):
            self.init_params = util.init_params_from_locals(locals())

            self._vSEP = Lfunction[index]['vSEP']
            self._vRatio = Lfunction[index]['vRatio']
            self._vEta = Lfunction[index]['vEta']
            self._totalBudget = totalBudget
            self.short_name = short_name

        def Run(self, Q, x, epsilon, seed):
            #split part of the privacy budget to calculate SEP and select parameters
            assert seed is not None, 'seed must be set'

            prng = np.random.RandomState(seed)

            assert len(x.shape)==1, '%s is defined for 1D data only' % self.__class__.__name__
        
            Ntotal = x.sum() + prng.laplace(loc= 0.0, scale=1.0 / (self._totalBudget * epsilon))
            epsilon = epsilon*(1- self._totalBudget)

            SEP =  Ntotal * epsilon

            self._ratio = float(np.interp(SEP,self._vSEP ,self._vRatio))
            self._eta = float(np.interp(SEP,self._vSEP ,self._vEta))
        
            return ahpr(x, epsilon, self._ratio, self._eta,prng)



def ahpr(x, epsilon, ratio, eta, prng, debug=False):

    assert prng, 'prng must be set'
    assert len(x.shape)==1, '%s is defined for 1D data only' % self.__class__.__name__

    x = np.array(x, float)

    # line 1: split epsilon
    assert 0 <= ratio and ratio <= 1
    eps1 = epsilon * ratio
    eps2 = epsilon * (1 - ratio)
    assert abs( (eps1 + eps2) - epsilon ) < 0.0000001
    n = len(x)

    # line 2: add noise
    noisyx = x + prng.laplace(0, 1/eps1, n)

    # line 3: threshold
    noisyx = threshold(noisyx, n, eta, eps1)

    # line 4: sort
    orig_indexes = noisyx.argsort()
    noisyx.sort()

    # line 5: cluster
    clusters = greedy_cluster(noisyx, eps2)

    # lines 6-9: add noise to groups and build new noisy x
    noisyx = {}    # use dict since we visit indices in unpredictable order
    for (i,j) in clusters:
        size = j - i   # cluster does not include j
        group = [orig_indexes[k] for k in range(i,j)]
        total = sum(x[i] for i in group)
        if debug:
            print 'group =', group, 'total =', total
        avg = (total + prng.laplace(0, 1/eps2)) / size
        for i in group:
            noisyx[i] = avg

    return np.array([noisyx[i] for i in range(n)])



def threshold(x, n, eta, eps1):
    '''values in x below threshold are set to zero'''
    cutoff = eta * math.log(n) / eps1
    return np.where(x <= cutoff, 0, x)

def simple_cluster(x):
    '''Puts in adjacent groups of 4'''
    tmp = x[:]
    groups = []
    group = []
    for val in x:
        group.append(val)
        if len(group) >= 4:
            groups.append(group)
            group = []
    groups.append(group)
    return groups

def sum_squared_error(P, PP, i, j):
    '''
    Returns sum of square for interval from i to j inclusive.

    Based on Optimal histograms with quality guarantees, VLDB 1998
    '''
    length = (j - i + 1)
    if i == 0:
        ss = PP[j]
        avg = P[j] / length
    else:
        ss = PP[j] - PP[i - 1]
        avg = (P[j] - P[i-1]) / length
    sse = ss - length * (avg ** 2)
    return sse

def err(P, PP, i, j, epsilon):
    '''
    Returns error of cluster that goes from i to j inclusive.
    '''
    sse = sum_squared_error(P, PP, i, j)
    length = (j - i + 1)
    error = sse + 2/(length * epsilon ** 2)
    return error


def err_star(x_j, P, j, epsilon):
    n = len(P)
    min_error = float('inf')
    last_error1 = last_error2 = None
    for l in range(j, n):
        length = l - j + 1
        if j == 0:
            C_jl = P[l] / length
        else:
            C_jl = (P[l] - P[j-1]) / length
        error1 = (x_j - C_jl) ** 2
        error2 = 2 / (length**2 * epsilon**2)

        # early termination (see p. 6 of paper)
        if l != j:
            A = error1 - last_error1
            B = last_error2 - 2 / ((n - j + 1)**2 * epsilon**2)
            if A >= B:
                break
        min_error = min(error1 + error2, min_error)
        last_error1 = error1
        last_error2 = error2
    return min_error


def greedy_cluster(x, epsilon):
    '''
    Returns list of (i,j) pairs denoting the contiguous clusters
    '''
    x = np.array(x, float)
    P = np.cumsum(x)      # prefix sum array
    PP = np.cumsum(x**2)  # prefix sum of squares

    clusters = []
    n = len(x)

    i = 0  # current cluster start
    j = 1  # potential cluster end
    while j < n:
        if (err( P, PP, i, j, epsilon ) >=
            err(P, PP, i, j-1, epsilon) + err_star(x[j], P, j, epsilon)):
            clusters.append( (i,j) )
            i = j
        j += 1
    clusters.append( (i,j) )  # don't forget last cluster
    return clusters


Lfunction ={ \
            'DEFAULT':{\
                'vSEP':[0, 50.0, 100.0,500.0,1000.0,10000.0,500000.0,1000000.0,5000000.0,10000000.0,100000000.0,1e+20],
                'vRatio':[0.7, 0.7, 0.7, 0.9, 0.9, 0.8, 0.7, 0.5, 0.5, 0.3, 0.3, 0.3],
                'vEta':[0.2, 0.2, 0.1, 0.2, 0.1, 0.1, 0.3, 0.1, 0.2, 0.1, 0.3, 0.3]},
            'POWER1':{\
                'vSEP':[0, 50.0, 100.0,500.0,1000.0,10000.0,500000.0,1000000.0,5000000.0,10000000.0,100000000.0,1e+20],
                'vRatio':[0.7, 0.7, 0.7, 0.9, 0.9, 0.8, 0.7, 0.5, 0.5, 0.3, 0.3, 0.3],
                'vEta':[0.2, 0.2, 0.1, 0.2, 0.1, 0.1, 0.3, 0.1, 0.2, 0.1, 0.3, 0.3]},
            'POWER2':{\
                'vSEP':[0, 50.0, 100.0,500.0,1000.0,10000.0,500000.0,1000000.0,5000000.0,10000000.0,100000000.0,1e+20],
                'vRatio':[0.8, 0.8, 0.7, 0.9, 0.9, 0.8, 0.6, 0.6, 0.5, 0.5, 0.3, 0.3],
                'vEta':[0.4, 0.4, 0.2, 0.1, 0.1, 0.1, 0.1, 0.2, 0.1, 0.3, 0.1, 0.1]}
        
}

# FROM THEIR IMPLEMENTATION (lamda is eta from paper)
# //const double eps=1;
# //const double rate=0.5;
# //const double lamda=0.4;
# //const double eps=0.1;
# //const double rate=0.85;
# //const double lamda=0.35;
# const double eps=0.01;
# const double rate=0.65;
# const double lamda=0.9;


