"""Implementation of greedy hierarchy engine."""
from __future__ import division
from builtins import map
from builtins import zip
from builtins import range
import itertools
import numpy
from scipy.linalg import block_diag
from dpcomp_core import util
from dpcomp_core.algorithm import estimate_engine 


class greedyH_engine(estimate_engine.estimate_engine):
    """Assign weights to hierarchical queries greedily according to the given
    workload. Answer weighted queries and generate an estimated dataset using
    least square estimator.
    This is only an estimate engine. Use greedyH_only_engine for GreedyH algorithm.
    """

    def __init__(self, branch=2, granu=100):
        """Setup the branching factor and granularity in numerical search.
        
        branch(2) - the branching factor of the hierarchy
        granu(100) - the granularity in numerical search
        """
        self.init_params = util.init_params_from_locals(locals())

        self._branch = branch
        self._granu = granu


    def Run(self, QtQ, x, epsilon, seed):
        """
        QtQ - given the workload Q in matrix form, QtQ is the
              multiplication between the transpose of Q and Q.
        """
        assert seed is not None, 'seed must be set'

        prng = numpy.random.RandomState(seed)

        x = numpy.array(x)
        assert len(x.shape)==1, '%s is defined for 1D data only' % self.__class__.__name__
        

        n = len(x)
        err, inv, dist, query = self._GreedyHierByLv(QtQ, n, 0, withRoot=False)
        qmat = []
        y2 = []
        for c in range(len(dist)):
            if dist[c] > 0:
                lb, rb = query[c]
                currow = numpy.zeros(n)
                currow[lb:rb+1] = dist[c]
                qmat.append(currow)
                y2.append(sum(x[lb:(rb+1)]) * dist[c])

        qmat = numpy.array(qmat)
        y2 += prng.laplace(0.0, util.old_div(1.0,epsilon), len(y2))

        return numpy.dot(inv, numpy.dot(qmat.T, y2))

    def _GreedyHierByLv(self, fullQtQ, n, offset, depth = 0, withRoot = False):
        """Compute the weight distribution of one node of the tree by minimzing
        error locally.
        
        fullQtQ - the same matrix as QtQ in the Run method
        n - the size of the submatrix that is corresponding
            to current node
        offset - the location of the submatrix in fullQtQ that
                 is corresponding to current node
        depth - the depth of current node in the tree
        withRoot - whether the accurate root count is given
        
        Returns: error, inv, weights, queries
        error - the variance of query on current node with epsilon=1
        inv - for the query strategy (the actrual weighted queries to be asked)
              matrix A, inv is the inverse matrix of A^TA
        weights - the weights of queries to be asked
        queries - the list of queries to be asked (all with weight 1)
        """
        if n == 1:
            return numpy.linalg.norm(fullQtQ[:, offset], 2)**2, \
                   numpy.array([[1.0]]), \
                   numpy.array([1.0]), [[offset, offset]]

        QtQ = fullQtQ[:, offset:offset+n]
        if (numpy.min(QtQ, axis=1) == numpy.max(QtQ, axis=1)).all():
            mat = numpy.zeros([n, n])
            mat.fill(util.old_div(1.0, n**2))
            return numpy.linalg.norm(QtQ[:,0], 2)**2, \
                   mat, numpy.array([1.0]), [[offset, offset+n-1]]

        if n <= self._branch:
            bound = list(zip(list(range(n)), list(range(1,n+1))))
        else:
            rem = n % self._branch
            step = util.old_div((n-rem), self._branch)
            swi = (self._branch-rem) * step
            sep = list(range(0, swi, step)) + list(range(swi, n, step+1)) + [n]
            bound = list(zip(sep[:-1], sep[1:]))

        serr, sinv, sdist, sq = list(zip(*[self._GreedyHierByLv
                                    (fullQtQ, c[1]-c[0], offset+c[0], 
                                    depth = depth+1) for c in bound]))
        invAuList = [c.sum(axis=0) for c in sinv]
        invAu = numpy.hstack(invAuList)
        k = invAu.sum()
        m1 = sum(map(lambda rng, v:
                     numpy.linalg.norm(numpy.dot(QtQ[:, rng[0]:rng[1]], v), 2)**2,
                     bound, invAuList))
        m = numpy.linalg.norm(numpy.dot(QtQ, invAu), 2)**2
        sumerr = sum(serr)

        if withRoot:
            return sumerr, block_diag(*sinv), \
                   numpy.hstack([[0], numpy.hstack(sdist)]), \
                   [[offset, offset+n-1]] + list(itertools.chain(*sq))

        decay = util.old_div(1.0, ( self._branch**(util.old_div(depth, 2.0))))
        err1 = numpy.array(list(range(self._granu, 0, -1)))**2
        err2 = numpy.array(list(range(self._granu)))**2 * decay
        toterr = 1.0/err1 * (sumerr - ((m-m1)*decay+m1) * err2 / (err1+err2*k))

        err = toterr.min() * self._granu**2
        perc = 1 - util.old_div(numpy.argmin(toterr), float(self._granu))
        inv = (util.old_div(1.0,perc))**2 * (block_diag(*sinv) 
              - (1-perc)**2 / ( perc**2 + k * (1-perc)**2 )
              * numpy.dot(invAu.reshape([n, 1]), invAu.reshape([1, n])))
        dist = numpy.hstack([[1-perc], perc*numpy.hstack(sdist)])
        return err, inv, dist, \
               [[offset, offset+n-1]] + list(itertools.chain(*sq))

