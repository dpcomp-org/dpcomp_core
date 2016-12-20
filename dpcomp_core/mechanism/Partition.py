import numpy
import numpy.ma as ma
import copy
"""
A partition is an array whose shape matches the domain of a data array.
Common values in a partition array indicate groups
E.g. [2, 5, 5, 2, 3] describes a partition consisting of 3 groups (e.g. positions 0 and 3 have "group id" 2)

Partitions can be 2D and 2D data arrays can be partitioned, as long as the partitioned output has a well-defined shape
    i.e. the 2D partition is a regular grid
    TODO: raise reasonable error if 2D partition is not grid


A Partition object provides methods for reduce and expand:

Reduce merges the groups specified in the partition vector, but in two different ways:
    - for a data vector, grouped columns (corresponding to cells) should be summed.
    - for a query (one row or many rows), grouped columns should be averaged.

Expand undoes a reduction, assuming uniformity within buckets.
    - for a data vector, uniform expansion is performed
    - for a query, a cell is expanded by copying the cell value into each position in the expanded group.


The actual values in the partition array don't matter for the definition of groups, however, when the partition is used
to reduce or split, the order may have an impact.

A partition may form groups over non-contiguous columns, so the order of groups in the reduced domain is not well-defined.

In particular, under reduction, a group becomes a column, and by default the new columns for each group will be placed
in order of the group-ids.  The Partition constructor includes a flag 'canonical_order' which, if set, will reorder
group-ids by first occurrence in the partition. In some cases, this preserves locality.

When reduce is followed by expand, the columns should be reformed in the same order (and this may be important
if we have workload queries defined over the original domain).

Reduce followed by expand is typically lossy; it is lossless only when:
    - a data vector is uniform within each group
    - a query has uniform coeffs in each cell of grouped cells, for all groups.

Queries that come from the original domain, and are reduced, should probably not be expanded back to the original
domain.  However, queries created over the reduced domain, may need to be expanded to the original domain and
this is lossless.
"""


class Partition(object):
    """
    Class holding a partition vector and providing helpful methods for using partitions.
    partition array may be n-dimensional, but is often flattened
    """

    def __init__(self, partition_array, canonical_order=False):
        """
        canonical_order will re-number the groups in the provided partition_array
        for locality.
        """
        self.vector = partition_array
        if canonical_order:
            self.vector = self.canonicalTransform(self.vector)

    def canonicalTransform(self,vector):
        """ transform a partition vector according to the canonical order.
         if bins are noncontiguous, use position of first occurrence.
         e.g. [3,4,1,1] => [1,2,3,3]; [3,4,1,1,0,1]=>[0,1,2,2,3,2]
        """
        unique, indices, inverse = numpy.unique(vector, return_index=True, return_inverse=True)
        uniqueInverse, indexInverse = numpy.unique(inverse,return_index =True)

        indexInverse.sort()
        newIndex = inverse[indexInverse]
        tups = list(zip(uniqueInverse, newIndex)) #replace uniqueInverse with unique if we want to use the exact numbers in partition vector
        tups.sort(key=lambda x: x[1])
        u = numpy.array( [u for (u,i) in tups] )
        vector = u[inverse].reshape(vector.shape)
        return vector

    def compose(self, p):
        ''' Return a new partition object which is the composition of self with input p
        '''
        # computing the composition is done by expanding the inner partition using the outer partition
        assert self.output_shape == p.input_shape, 'Composition of mis-matched partitions. Output shape {} should match input shape {}'.format(self.output_shape, p.input_shape)
        p = p.vector
        expanded = self.expand_query(p)
        return Partition(expanded)

    def deviation(self, x, epsilon2 = None):
        '''
        Compute DAWA partition score
            the deviation when using this partition to reduce and estimate data
        This is the error that would be experienced after reduction and knowing true bucket counts for x.
        epsilon2 is the estimated noise factor.  Ignored by default to return just the raw deviation
        '''
        estimated = self.expand_data( self.reduce_data(x) )     # reduce then expand
        deviation = sum(abs(x - estimated))
        if epsilon2:
            deviation += self.output_size / float(epsilon2)
        return deviation

    @property
    def ndim(self):
        return self.vector.ndim

    @property
    def size(self):
        # this is input size
        return self.vector.size

    @property
    def output_size(self):
        return numpy.prod(self.output_shape)

    @property
    def input_shape(self):
        """
        Size of original domain the partition will apply to
        """
        return self.vector.shape

    @property
    def output_shape(self):
        # TODO: this won't work for n-dim partitions that are irregular (will work for grids)
        # derive output shape from partition_vector (count num. of unique values along each axis)
        if self.vector.ndim == 1:
            return (len(numpy.unique(self.vector)), )
        else:
            out = [len(numpy.unique(numpy.compress([True], self.vector, axis=i))) for i in range(self.ndim)]
            out.reverse()   # rows/cols need to be reversed here
            return tuple(out)

    @property
    def max_partition_size(self):
        unique, unique_counts = numpy.unique(self.vector, return_counts=True)
        return max(unique_counts)

    def __str__(self):
        return '<' + self.__class__.__name__ + '>' + ' from shape %s' % str(self.input_shape) + ' to %s' % str(self.output_shape) + '\n' + str(self.vector)

    ###########################
    ### reducing operations
    ###########################

    def reduce_data(self, x):
        """
        :param x: data vector x, possibly n-dimensional, same shape as self
        :return: transformed x in which grouped cells have been *added* together
        """
        assert x.shape == self.input_shape, 'Shape of x <%s> and shape of partition vector <%s> must match.' \
                                                  % (str(x.shape), str(self.input_shape))

        return self.reduce_helper(x, 'SUM').reshape(self.output_shape)

    def reduce_query(self,q):
        """
        :param q: a single query in the form of a np array, could be a 1D-vector, or higher n-dimensional array
        :return: transformed q in which grouped cells have been averaged together"""
        assert q.shape == self.input_shape, 'Shape of q <%s> and shape of partition vector <%s> must match.' \
                                                  % (str(q.shape), str(self.input_shape))
        return self.reduce_helper(q, 'AVG').reshape(self.output_shape)

    def reduce_workload(self, w):
        """
        :param w: workload, a list of queries, shape of each query much match the input size of partition vector.
        :return: transformed w in which grouped cells have been averaged together
        """
        for q in w:
            assert q.shape == self.input_shape, 'Mismatch between query size in workload and partition vector'
        return numpy.array([self.reduce_query(q) for q in w])

    ###########################
    ### expanding operations
    ###########################

    def expand_data(self, y):
        # number of unique values in partition_vector should match number of columns in x
        # because x should be in the reduced domain implied by partition vector
        assert self.output_shape == y.shape
        return self.expand_helper(y,expand_type='AVG')#.reshape(self.input_shape)

    def expand_query(self, q):
        """
        :param q: a single query in the form of a np array, could be a 1D-vector, or higher n-dimensional array
        :return: transformed w in which grouped cells have been averaged together"""
        assert q.shape == self.output_shape, 'Mismatch between query size and partition vector'
        #return numpy.apply_along_axis(self.expand_helper, 1, w, 'COPY')
        return self.expand_helper(q,expand_type='COPY')
   
    def expand_workload(self, w):
        """
        :param w: workload, a list of queries, shape of each query much match the input size of partition vector.
        :return: transformed w in which grouped cells have been averaged together
        """
        for q in w:
            assert q.shape == self.output_shape, 'Mismatch between query size in workload and partition vector'
        return numpy.array([self.expand_query(q) for q in w])
    
    ######################################################
    ### projecting operations and reverse project (for split/ merger operator)
    ######################################################
    @staticmethod
    def project(x,mask):
        """undo projection. All the cells which were masked in projection gets assigned a zero.
            e.g. mask = [0,0,1,1] project on the first two columns of x.
        """
        assert len(x) == len(mask), "Projection mask and vector has different shape"

        mx = ma.masked_array(x, mask=mask)
        return mx.compressed()

    @staticmethod
    def unproject(projx,mask):
        """undo projection. All the cells which were masked in projection gets assigned a zero.
            e.g. with projx = [1,2,3,4], and mask = [0,0,1,1,0,0], return x = [1,2,0,0,3,4]
        """
        mask = copy.copy(mask)
        x = ma.array(numpy.zeros_like(mask),mask = mask)
        x[~x.mask] = projx
        return x.data


    @staticmethod
    def project_workload(W,mask):
        """project workload or a list of measurements"""
        return numpy.array([project(q,mask) for q in W])

    @staticmethod
    def unproject_workload(W,mask):
        """unproject a list of measurements"""
        return numpy.array([unproject(q,mask) for q in W])

    

    ###########################
    ### helper functions
    ###########################

    def reduce_helper(self, x, aggregate_type):
        """
        aggregate_type should be 'SUM' or 'AVG
        """
        unique, indices, inverse, counts = numpy.unique(self.vector, return_index=True, return_inverse=True, return_counts=True)
        res = numpy.zeros_like(unique, dtype=float)
        for index, c in numpy.ndenumerate(x.ravel()):   # needs to be flattened for parallel indexing with output of unique
            if aggregate_type == 'SUM':
                res[ inverse[index] ] += c
            elif aggregate_type == 'AVG':
                res[ inverse[index] ] += c / counts[inverse[index]]
            else:
                assert False, 'Invalid aggregate_type'
        return numpy.array(res)

    def expand_helper(self, y, expand_type):
        unique, index, inverse = numpy.unique(self.vector, return_index=True, return_inverse=True)
        x = numpy.zeros_like(self.vector, dtype=float)
        for (i,u) in enumerate(unique):
            if expand_type == 'AVG':
                x[self.vector==u] = float(y.ravel()[i]) / (self.vector==u).sum()
            elif expand_type == 'COPY':
                x[self.vector==u] = float(y.ravel()[i])
            else:
                assert False, 'Invalid expand_type'
        return x



"""
Some simple partitions, useful for testing
"""

def partition_unit_groups(n):
    """ Return a no-op partition in which there is one partition per cell (domain size n) """
    return Partition( numpy.array(range(n)) )

def partition_unit_groups_2d(shape):
    """ Return a no-op partition in which there is one partition per cell, matching shape """
    return Partition( numpy.arange(numpy.product(shape)).reshape(shape) )

def partition_one_group(n):
    """ Return a partition which groups all cells into one group (domain size n) """
    return Partition( numpy.ones( (n,), dtype=int ))

def partition_one_group_2d(shape):
    """ Return a partition which groups all cells into one group, matching shape """
    return Partition( numpy.ones( shape, dtype=int ))



if __name__ == '__main__':
    pass
