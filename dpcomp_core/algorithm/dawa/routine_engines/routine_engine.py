"""General engine for Data- and Workload-Aware algorithms."""
from __future__ import division
from builtins import str
from builtins import range
from builtins import object
import bisect
import itertools
import numpy
import hashlib
from dpcomp_core import util
from dpcomp_core import workload

#@register('default')
class routine_engine(object):
    """General two-step engine without workload transform."""

    def __init__(self, p_engine = None, e_engine = None, ratio = 0.5):
        """Setting up engines for each step.
        
        partition_engine - the class for data aware paritioning
        query_enging - the class for counts querying
        ratio - the ratio of privacy budget used for the partition engine
        """
        self._partition_engine = p_engine
        self._estimate_engine = e_engine
        self._ratio = ratio
    
    def _DirectRun(self, Q, x, epsilon):
        """Run a estimate engine without a partition engine"""
        return self._estimate_engine.Run(Q, x, epsilon)

    def asDict(self):
        d = util.class_to_dict(self)
        return d

    def analysis_payload(self):
        return util.class_to_dict(self)

    @property
    def key(self):
        """ Using leading 8 characters of hash as key for now """
        return self.hash[:8]


    @property
    def hash(self):
        """
        Uniqueness of this hash relies on subclasses writing init parameters as instance variables
        """
        m = hashlib.sha1()
        m.update(util.prepare_for_hash(self.__class__.__name__))
        m.update(util.prepare_for_hash(self._estimate_engine.__class__.__name__))
        m.update(util.prepare_for_hash(self._partition_engine.__class__.__name__))
        m.update(util.prepare_for_hash(str(util.standardize(sorted(self.init_params.items())))))
        return m.hexdigest()

    def Run(self, Q, x, epsilon,seed):
        """Run three engines in order with given epsilons to estimate a
        dataset x to answer query set Q
        
        Q - the query workload
        x - the underlying dataset
        epsilon - the total privacy budget
        """
        assert seed is not None, 'seed must be set'
        prng = numpy.random.RandomState(seed)

        n = len(x)

        pSeed = prng.randint(500000)
        eSeed = prng.randint(500000)

        if self._partition_engine is None:
            # ignore ratio when partition_engine is omitted
            return self._DirectRun(Q, x, epsilon,eSeed)
        else:
            if self._ratio < 0 or self._ratio >= 1:
                raise ValueError('ratio must in range [0, 1)')

            partition = self.Compute_partition(x, epsilon,pSeed)
            # check that partition buckets span domain
            assert min(itertools.chain(*partition)) == 0
            assert max(itertools.chain(*partition)) == (n-1)

            eps2 = (1-self._ratio) * epsilon   # this is epsilon_2 used in paper (the epsilon for estimation)
            devs = abs( numpy.array(x) - (util.old_div(sum(x), float(len(x)))) )

            counts = self._estimate_engine.Run(
                        self._workload_reform(Q, partition, n),
                        self._dataset_reform(x, partition),
                        epsilon*(1-self._ratio),eSeed)
            return self._rebuild(partition, counts, n)

    def Get_Partition(self):
        """Get the data dependent partition"""
        return self._partition

    def Compute_partition(self, x, epsilon,pSeed):
        """Compute the data dependent partition."""
        if self._ratio == 0:
            # use identity partition if no privacy budget is
            # reserved for partitioning
            self._partition = [[c, c] for c in range(n)]
        else:
            self._partition = self._partition_engine.Run(x, epsilon,
                                                         self._ratio,pSeed)

        return self._partition

    @staticmethod
    def _workload_reform(Q, partition, n):
        pass

    @staticmethod
    def _dataset_reform(x, partition):
        """Reform a dataset x0 into x with a given parition."""
        return [sum(x[lb:(rb+1)]) for lb, rb in partition]
        
    @staticmethod
    def _rebuild(partition, counts, n):
        """Rebuild an estimated data using uniform expansion."""
        estx = numpy.zeros(n)
        n2 = len(counts)
        for c in range(n2):
            lb, rb = partition[c]
            estx[lb:(rb+1)] = util.old_div(counts[c], float(rb - lb + 1))

        return estx


#@register('transformQ')
class transform_engine_q(routine_engine):
    """The engine with workload reform implemented."""

    @staticmethod
    def _workload_reform(Q0, partition, n):
        """Reform a workload Q0 into Q with a given parition,

        Q0 - the workload to be reformed
        partition - the given partition
        n - the size of the original domain

        An example of query reform: 
        Give a dataset with size 4, and partition is [[0], [1, 2, 3]],
        Then query x1+x2+x3+x4 will be converted to y1+y2
             query x1+x2 will be converted y1+(1/3)y2
        """
        partition_lb, partition_rb = zip*(partition)
        Q = []
        for q in Q0:
            q1 = []
            for wt, lb, rb in q:
                lpos = bisect.bisect_left(partition_rb, lb)
                rpos = bisect.bisect_left(partition_lb, rb)
                if lpos == rpos:
                    q1.append([wt*(rb-lb+1.0)
                               /(partition_rb[lpos]-partition_lb[lpos]+1.0),
                               lpos, rpos])
                else:
                    q1.append([wt*(partition_rb[lpos]-lb+1.0)
                               /(partition_rb[lpos]-partition_lb[lpos]+1.0),
                               lpos, lpos])
                    q1.append([wt*(rb-partition_lb[rpos]+1.0)
                               /(partition_rb[rpos]-partition_lb[rpos]+1.0),
                               rpos, rpos])
                    if lpos + 1 < rpos:
                        q1.append([wt, lpos+1, rpos-1])

            Q.append(q1)

        return Q


#@register('transformQtQ')
class transform_engine_qtqmatrix(routine_engine):
    """The engine that outputs the matrix form of Q^TQ in workload reform."""

    def __init__(self, p_engine = None, e_engine = None, \
                 ratio = 0.5, max_block_size = None):
        """Setting up engines for each step.
        
        partition_engine - the class for data aware paritioning
        query_enging - the class for counts querying
        ratio - the ratio of privacy budget for partitioning
        max_block_size - parameter for workload_reform, see below for details.
        """
        self._max_block_size = max_block_size
        super(transform_engine_qtqmatrix, self).__init__(p_engine, e_engine, ratio)

    def _DirectRun(self, Q, x, epsilon,seed):
        """Run a estimate engine without a partition engine"""
        n = len(x)
        partition = [[c,c] for c in range(n)]
        return self._estimate_engine.Run(
            self._workload_reform(Q, partition, n), x, epsilon,seed)

    def _workload_reform(self, Q0, partition, n):
        """Reform a workload Q0 into Q with a given partition,
        and output Q^TQ

        max_block_size - the max number of rows to be materialized
                         when computing Q^TQ. Set to n if omitted.
        """

        if isinstance(Q0, workload.Workload):
            Q0 = Q0.query_list
        n = partition[-1][-1] + 1
        n2 = len(partition)
        QtQ = numpy.zeros([n2, n2])
        if self._max_block_size is None:
            max_block_size = n
        else:
            max_block_size = self._max_block_size

        cnum = list(range(0, len(Q0), max_block_size))

        for c0 in cnum:
            nrow = min(len(Q0)-c0, max_block_size)
            Q0mat = numpy.zeros([nrow, n])

            for c in range(nrow):
                for qRange in Q0[c+c0].ranges:
                    Q0mat[c, qRange.lb[0]:qRange.ub[0]+1] = qRange.wgt

            Qmat = numpy.zeros([nrow, n2])
            for c in range(n2):
                lb, rb = partition[c]
                Qmat[:, c] = Q0mat[:, lb:(rb+1)].mean(axis=1)

            QtQ += numpy.dot(Qmat.T, Qmat)

        return QtQ


#@register('transformQtQlinear')
class transform_engine_qtqmatrix_linear(transform_engine_qtqmatrix):
    """The engine that outputs the matrix form of Q^TQ in workload reform.

    This version expects a matrix of linear queries.
    """

    def __init__(self, p_engine = None, e_engine = None, \
                 ratio = 0.5):
        super(transform_engine_qtqmatrix_linear, self).__init__(p_engine, e_engine, ratio, None)

    def _workload_reform(self, Q0, partition, n):
        """Reform a workload Q0 into Q with a given parition,
        and output Q^TQ
        """
        # check for type of Q0
        if isinstance(Q0, workload.Workload):
            Q0 = Q0.query_list
        if len(Q0.shape) == 3:  # total hack: if the workload is range queries, then first tfm them to matrix
            # run "old" code (transform_engine_qtqmatrix) and save result to compare against
            QtQold = super(transform_engine_qtqmatrix_linear, self)._workload_reform(Q0, partition, n)
            Q0 = as_matrix(Q0, n)
        else:
            QtQold = None

        assert (partition[-1][-1] + 1) == n  # these should be equal, not sure why Chao computes n from partition?
        n2 = len(partition)
        QtQ = numpy.zeros([n2, n2])
        
        nrow = len(Q0)
        Q0mat = Q0

        # Qmat is reduced query matrix: queries over buckets of partition
        Qmat = numpy.zeros([nrow, n2])
        # iterate by columns of Qmat
        for c in range(n2):
            lb, rb = partition[c]  # column c of Qmat represents query weight on c^th partition
            Qmat[:, c] = Q0mat[:, lb:(rb+1)].mean(axis=1)  # query weight is average of weights on bins in that partition

        QtQ += numpy.dot(Qmat.T, Qmat)

        if QtQold is not None:  # debugging purposes: compare against transform_engine_qtqmatrix
            assert (QtQold == QtQ).all()
        return QtQ

def as_matrix(Q, n):
    """
    Takes Q, a collection of m queries, in 1d range query form and returns an m x n workload matrix
    """

    m = len(Q)
    Qmat = numpy.zeros((m,n))
    for i in range(m):
        wt, lb, rb = Q[i][0]
        Qmat[i, lb:rb+1] = wt
    return Qmat
