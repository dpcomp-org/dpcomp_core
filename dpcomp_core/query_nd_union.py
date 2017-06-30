from builtins import zip
from builtins import object
import numpy
import collections

'''
    Class ndRangeUnion
    representing n-dimensional range queries, including queries consisting of unions of ranges
    
    A query consists of a list of 'ndRange' namedtuples with fields: lb, ub, wgt
    where:
        lb is a n-dim tuple representing the lower corner
        ub is a n-dim tuple representing the upper corner
        wgt is a scalar weight for the range

    Example: ndRange(lb=(1, 1), ub=(2, 3), wgt=2.0) 
    
    Given an n-dimensional numpy array, a range query is evaluated by summing the values in the given n-dimensional range and scaling by 'wgt'.
    If the query consists of multiple ranges (i.e. a union) its value is the sum of the values of each range. 

    USAGE 
    This builds a two-dimensional range-union with two unioned ranges:
        q = ndRangeUnion() 
        q.addRange( (0,1), (2,3), wgt=1.0 )
        q.addRange( (2,2), (0,4), wgt=2.0 )
    This builds a one-dimensional range query:
        q = ndRangeUnion() 
        q.add1DRange( 0, 10, wgt=1.0 )

    Note: 
        the semantics of a single range [lb_i,ub_i] is inclusive: it sums the counts in positions lb_i, lb_(i+1), ... ub_i 
        For example [1, (0,1)] is a one dimensional range query with weight 1, that sums both positions 0 and 1.
        This differs from standard python range definitions (e.g. array[0,1].sum() would sum only position 0)

    Note: 
        there is currently no checking for overlapping ranges when adding a range to form a union.
        query evaluation is okay with overlapping ranges, but other things done with slices may not be what is expected

'''


ndRange = collections.namedtuple('ndRange', 'lb ub wgt')

class ndRangeUnion(object):

    def __init__(self):
        self.ranges = []    # a list of multi-dim range queries, each is ndRange named tuple
        self.ndim = None    # number of dimensions of each query
        self.impliedShape = None    # the smallest domain size for which queries are valid (based on max ranges) (like numpy array .shape)

    def addRange(self, lb, ub, wgt=1.0):
        ''' Add an ndRange object to the union '''
        assert len(lb) == len(ub), 'Dimensions of upper and lower corners must match.'
        assert all( l <= u for (l,u) in zip(lb,ub) ), 'Lower corner must be <= upper corner'
        if not self.ranges:
            self.ndim = len(lb)
            self.impliedShape = tuple([i+1 for i in ub])       # add 1 to each pos
        else: # list is not empty
            assert len(lb) == self.ndim, 'Dimensions of unioned range queries must match.'
            self.impliedShape = tuple( [max(new+1,old) for new, old in zip(ub,self.impliedShape)] )
        self.ranges.append( ndRange(lb,ub,wgt) )
        return self

    def add1DRange(self, lb, ub, wgt=1.0):  # short-cut for creating 1D range using ints
        assert type(lb)==int and type(ub)==int, 'Expected ints for 1D Range query'
        self.addRange((lb,), (ub,), wgt)
        return self

    @staticmethod
    def slice(range):
        ''' Return slice object for indexing ndarrays based on a given ndRange. '''
        return [slice(i,j+1) for (i,j) in zip(range.lb,range.ub)]

    def _validateShape(self, shape):
        ''' Return true if input 'shape' tuple is valid for this range query (correct no. of dims, no out of bounds indexes) '''
        assert len(shape) == self.ndim, 'Number of dimensions differ: shape is: %s while query has ndim: %i' % (shape, self.ndim)
        assert all( [maxub <= s for maxub,s in zip(self.impliedShape,shape)] )
        return True

    def eval(self, x):
        ''' Evaluate self on input data x '''
        self._validateShape(x.shape)
        return sum( [r.wgt * x[ndRangeUnion.slice(r)].sum() for r in self.ranges] )     # sum the results of the individual ranges

    def asArray(self, shape=None):
        ''' Return ndarray representing query
            Optionally can be in provided shape o.w. will use impliedShape
        '''
        if shape:
            self._validateShape(shape)
        else:
            shape = self.impliedShape
        array = numpy.zeros(shape)
        for r in self.ranges:
            array[ndRangeUnion.slice(r)] += r.wgt
        return array

    def sens(self):
        '''return sensitivity of query'''
        return numpy.max(numpy.absolute(self.asArray()))

    def __repr__(self):
        rep = "<%iD RangeQueryUnion:" % self.ndim
        for r in self.ranges:
            rep += ' ->' + r.__repr__() 
        return rep + '>'

