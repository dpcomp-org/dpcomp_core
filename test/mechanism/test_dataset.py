
"""Unit test for dataset_new.py"""

import numpy
from dpcomp_core.mechanism import dataset
import unittest

dnames = [ 'ADULTFRANK', 'HEPTH', 'INCOME', 'MEDCOST', 'NETTRACE', 'PATENT', 'SEARCHLOGS']

class DatasetTests(unittest.TestCase):


    def setUp(self):
        n = 1024
        scale = 1E5
        self.hist = numpy.array( range(n))
        self.d = dataset.Dataset(self.hist, None)
        self.dist = numpy.random.exponential(1,n)
        self.dist = self.dist / float(self.dist.sum())
        self.ds = dataset.DatasetSampled(self.dist, scale, None, 1001)

    def testDataset(self):
        self.assertEqual( self.hist.sum(), self.d.scale)
        self.assertEqual( self.hist.max(), self.d.maxCount)
        print self.d.asDict()


    def testDatasetReduce(self):
        div = 4
        new_shape = (self.hist.shape[0]/div,)
        dr = dataset.Dataset(hist=self.hist, reduce_to_domain_shape=new_shape)
        self.assertEqual(dr.domain_shape,new_shape)

    def testDataset2D(self):
        self.X2 = dataset.DatasetSampledFromFile(nickname='SF-CABS-S', sample_to_scale=1000, reduce_to_dom_shape = (32,32),  seed=111)


    def testDatasetSampled(self):
        print self.ds.asDict()

    def testZero(self):
        ''' Sampled data has zero counts in buckets that were originally zero '''
        for name in dnames:
            loaded = dataset.load(dataset.filenameDict[name])
            sampled = dataset.DatasetSampledFromFile(name, 1E4, reduce_to_dom_shape=None, seed=1002).payload
        self.assertEqual( len(loaded), len(sampled) )
        for i in range(len(loaded)):
            if loaded[i] == 0:
                self.assertEqual( sampled[i], 0, 'failure on %s' % name )





if __name__ == "__main__":
    unittest.main(verbosity=2)   
