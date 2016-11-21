"""Unit test for AG_noisy.py"""

import numpy
from dpcomp_core.monolithic import AG_noisy
from dpcomp_core.mechanism import workload 
from dpcomp_core.mechanism import dataset
import unittest

class AGNOisyTests(unittest.TestCase):


    def setUp(self):
        self.d2D = dataset.DatasetSampledFromFile(nickname='SF-CABS-S', sample_to_scale=1000, reduce_to_dom_shape = (32,32),  seed=111)
    
        self.epsilon = 0.1
        self.w2D = workload.Identity((32,32))
        self.eng = AG_noisy.AG_engine_Noisy()

    def testRandom(self):

        seed = 1
        h1 = self.eng.Run(self.w2D,self.d2D.payload,self.epsilon,seed)
        h2 = self.eng.Run(self.w2D,self.d2D.payload,self.epsilon,seed)

        self.assertSequenceEqual(list(h1.flatten()),list(h2.flatten()))

        numpy.random.seed(100)#see if setting numpy seed would affect random state object prng

        h3 = self.eng.Run(self.w2D,self.d2D.payload,self.epsilon,seed)
        self.assertSequenceEqual(list(h1.flatten()),list(h3.flatten()))

if __name__ == "__main__":
    unittest.main(verbosity=2)   
