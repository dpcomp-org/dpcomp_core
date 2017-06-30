from __future__ import division
from builtins import str
import numpy
import os
import sys
import logging
from dpcomp_core.algorithm.dawa.cutils import cutil
from dpcomp_core.algorithm.dawa.partition_engines import partition_engine
from dpcomp_core import util


class l1partition_engine(partition_engine.partition_engine):
    """Use the L1 partition method."""

    def __init__(self):
        self.init_params = util.init_params_from_locals(locals())

    @staticmethod
    def Run(x, epsilon, ratio,seed):
        return L1partition(x, epsilon, ratio, gethist=True,seed =seed)


class l1partition_approx_engine(partition_engine.partition_engine):
    """Use the approximate L1 partition method."""

    def __init__(self):
        self.init_params = util.init_params_from_locals(locals())
        
    @staticmethod
    def Run(x, epsilon, ratio,seed):
        return L1partition_approx(x, epsilon, ratio, gethist=True,seed = seed)


def L1partition(x, epsilon, ratio=0.5, gethist=False,seed=None):
    """Compute the noisy L1 histogram using all interval buckets

    Args:
        x - list of numeric values. The input data vector
        epsilon - double. Total private budget
        ratio - double in (0, 1). use ratio*epsilon for partition computation and (1-ratio)*epsilon for querying
                the count in each partition
        gethist - boolean. If set to truth, return the partition directly (the privacy budget used is still ratio*epsilon)

    Return:
        if gethist == False, return an estimated data vector. Otherwise, return the partition
    """
    assert seed is not None, "seed must be set"
    prng = numpy.random.RandomState(seed)

    assert (x.dtype == numpy.dtype(int) or x.dtype == numpy.dtype("int32")), "Input vector must be int! %s given" %x.dtype
    y=x.astype('int32') #numpy type int32 is not not JSON serializable
    check = (x ==y)
    assert check.sum() == len(check), "Casting error from int to int32"
    x=y

    n = len(x)
    hist = cutil.L1partition(n+1, x, epsilon, ratio, prng.randint(500000))
    hatx = numpy.zeros(n)
    rb = n
    if gethist:
        bucks = []
        for lb in hist[1:]:
            bucks.insert(0, [lb, rb-1])
            rb = lb
            if lb == 0:
                break
        logging.debug('  L1-PART: number of buckets %s' % str(bucks[:5]) )                   
        return bucks
    else:
        for lb in hist[1:]:
            hatx[lb:rb] = util.old_div(max(0, sum(x[lb:rb]) + prng.laplace(0, util.old_div(1.0,(epsilon*(1-ratio))), 1)), float(rb - lb))
            rb = lb
            if lb == 0:
                break

        return hatx


def L1partition_approx(x, epsilon, ratio=0.5, gethist=False,seed =None):
    """Compute the noisy L1 histogram using interval buckets of size 2^k

    Args:
        x - list of numeric values. The input data vector
        epsilon - double. Total private budget
        ratio - double in (0, 1) the use ratio*epsilon for partition computation and (1-ratio)*epsilon for querying
                the count in each partition
        gethist - boolean. If set to truth, return the partition directly (the privacy budget used is still ratio*epsilon)

    Return:
        if gethist == False, return an estimated data vector. Otherwise, return the partition
    """
    assert seed is not None, "seed must be set"
    prng = numpy.random.RandomState(seed)

    n = len(x)
    # check that the input vector x is of appropriate type
    assert (x.dtype == numpy.dtype(int) or x.dtype == numpy.dtype("int32")), "Input vector must be int! %s given" %x.dtype
    y=x.astype('int32') #numpy type int32 is not not JSON serializable
    check = (x ==y)
    assert check.sum() == len(check), "Casting error from int to int32"
    x=y

    hist = cutil.L1partition_approx(n+1, x, epsilon, ratio, prng.randint(500000))
    hatx = numpy.zeros(n)
    rb = n
    if gethist:
        bucks = []
        for lb in hist[1:]:
            bucks.insert(0, [lb, rb-1])
            rb = lb
            if lb == 0:
                break
              
        return bucks
    else:
        for lb in hist[1:]:
            hatx[lb:rb] = util.old_div(max(0, sum(x[lb:rb]) + prng.laplace(0, util.old_div(1.0,(epsilon*(1-ratio))), 1)), float(rb - lb))
            rb = lb
            if lb == 0:
                break

        return hatx
