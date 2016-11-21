import copy
import hashlib
import itertools
import numpy
from dpcomp_core.mixins import Marshallable
from dpcomp_core.mechanism.query_nd_union import ndRangeUnion
from dpcomp_core import util


"""
These classes define workloads
"""

class Workload(Marshallable):

    def __init__(self, query_list, domain_shape):
        """ Basic constructor takes list of ndQuery instances and a domain shape
        """
        self.domain_shape = domain_shape
        self.query_list = query_list
        self._matrix = None
        self._compiled = False

    def compile(self):
        if not self._compiled:
            self.compute_matrix() 
            self._compiled = True

        return self

    @property
    def matrix(self):
        return self.compile()._matrix

    @property
    def size(self):
        return len(self.query_list)

    def compute_matrix(self):
        rows = [r.asArray(self.domain_shape).flatten() for r in self.query_list]
        n = rows[0].size
        m = len(rows)
        self._matrix = numpy.empty(shape=(m,n))

        for (i,row) in enumerate(rows):
            self._matrix[i,:] = row

        return self._matrix

    def sensitivity(self):
        # copied from utilities.py
        ''' Compute sensitivity of a collection of ndRangeUnion queries '''
        maxShape = tuple( [max(l) for l in zip(*[q.impliedShape for q in self.query_list])] )
        array = numpy.zeros(maxShape)
        for q in self.query_list:
            array += q.asArray(maxShape)
        return numpy.max(array)

    def sensitivity_from_matrix(self):
        """Return the L1 sensitivity of input matrix A: maximum L1 norm of the columns."""
        return float(numpy.linalg.norm(self.matrix, 1))   # implemented in numpy as 1-norm of matrix

    def evaluate(self, x):
        return numpy.dot(self.matrix, x.ravel())

    @property
    def key(self):
        """ Using leading 8 characters of hash as key for now """
        return self.hash[:8]

    def asDict(self):
        d = util.class_to_dict(self, ignore_list=['matrix','_matrix','query_list', '_compiled'])
        ## add decomposed shape attrs ??
        return d

    def analysis_payload(self):
        return util.class_to_dict(self, ignore_list=['matrix','_matrix','query_list', '_compiled'])


class Identity(Workload):
    """ Identity workload for in k-dimensional domain """

    def __init__(self, domain_shape, weight=1.0, pretty_name='identity'):
        self.weight = weight
        self.pretty_name = pretty_name

        indexes = itertools.product(*[range(i) for i in domain_shape])   # generate index tuples
        queries = [ndRangeUnion().addRange(i,i,weight) for i in indexes]
        super(self.__class__,self).__init__(queries, domain_shape)

    @classmethod
    def oneD(cls, domain_shape_int, weight=1.0):
        return cls((domain_shape_int,), weight)
    @property
    def hash(self):
        m = hashlib.sha1()
        m.update(self.__class__.__name__)
        m.update(str(self.weight))
        m.update(str(util.standardize(self.domain_shape)))
        return m.hexdigest()

class Prefix1D(Workload):
    """ Workload of all 1D range queries with left bound equal to 0
        (Prefix is not well-defined in higher dimensions)
    """

    def __init__(self, domain_shape_int, pretty_name='prefix 1D'):
        self.init_params = util.init_params_from_locals(locals())

        self.pretty_name = pretty_name

        queries = [ndRangeUnion().add1DRange(0, c, 1.0) for c in range(domain_shape_int)]
        super(self.__class__,self).__init__(queries, (domain_shape_int,))

    def __repr__(self):
        r = self.__class__.__name__ + '('
        r += 'domain_shape_int=' + str(self.domain_shape[0]) + ')'
        return r

    @property
    def hash(self):
        m = hashlib.sha1()
        m.update(self.__class__.__name__)
        m.update(str(util.standardize(self.domain_shape)))
        return m.hexdigest()


class RandomRange(Workload):
    ''' Generate m random n-dim queries, selected uniformly from list of shapes and placed randomly in n-dim domain
        shape_list: list of shape tuples
        domain_shape: a shape tuple describing domain
        m: number of queries in result
        Note: for 1-dim, shapes must be unary tuples, e.g. (2,) (or see convenience method below)
    '''

    def __init__(self, shape_list, domain_shape, size, seed=9001, pretty_name='random range'):
        self.init_params = util.init_params_from_locals(locals())

        self.shape_list = copy.deepcopy(shape_list)
        self.seed = seed
        self.pretty_name = pretty_name
        self._size = size

        prng = numpy.random.RandomState(seed)
        if shape_list == None:
            shapes = randomQueryShapes(domain_shape, prng)
        else:
            prng.shuffle(self.shape_list)
            shapes = itertools.cycle(self.shape_list) # infinite iterable over shapes in shape_list
        queries = []
        for i in range(size):
            lb, ub = placeRandomly(shapes.next(), domain_shape, prng)       # seed must be None or repeats
            queries.append( ndRangeUnion().addRange(lb,ub,1.0) )
        super(self.__class__,self).__init__(queries, domain_shape)

    @property
    def hash(self):
        m = hashlib.sha1()
        m.update(self.__class__.__name__)
        m.update(str(self._size))
        m.update(str(util.standardize(self.shape_list)))
        m.update(str(util.standardize(self.domain_shape)))
        return m.hexdigest()

    @classmethod
    def oneD(cls, shape_list, domain_shape_int, size, seed=9001):
        ''' Convenience method allowing ints to be submitted in 1D case '''
        return cls([(i,) for i in shape_list], (domain_shape_int,), size, seed)

def randomQueryShapes(domain_shape, prng):
    ''' Generator that produces a list of range shapes; can be passed as iterator
        domain_shape: is the shape tuple of the domain
        prng: is numpy RandomState object
    '''
    while True:
        shape = [prng.randint(1, dim+1, None) for dim in domain_shape]
        yield tuple(shape)

def placeRandomly(query_shape, domain_shape, prng=None):
    ''' Place a n-dim query randomly in n-dim domain
        Return lb tuple and ub tuple which can be used to construct a range query object
    '''
    if not prng:
        prng = numpy.random.RandomState()

    lb, ub = [], []
    for i, val in enumerate(query_shape):
        lower = prng.randint(0, domain_shape[i] - query_shape[i] + 1, None)
        lb.append(lower)
        ub.append(lower + query_shape[i] - 1)
    return tuple(lb), tuple(ub)


