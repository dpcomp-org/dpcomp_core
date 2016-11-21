"""Unit test for identity.py"""

import numpy
from dpcomp_core.monolithic import identity
from dpcomp_core.mechanism import workload 
from dpcomp_core.mechanism import dataset
import unittest

dnames = [ 'ADULTFRANK', 'HEPTH', 'INCOME', 'MEDCOST', 'NETTRACE', 'PATENT', 'SEARCHLOGS']

class IdentityTests(unittest.TestCase):


    def setUp(self):
        n = 1024
        self.hist = numpy.array( range(n))
        self.d = dataset.Dataset(self.hist, None)
        self.dist = numpy.random.exponential(1,n)
        self.dist = self.dist / float(self.dist.sum())
    
        self.epsilon = 0.1
        self.w1 = workload.Identity.oneD(1024 , weight=1.0)
        self.w2 = workload.Prefix1D(1024)
        self.eng = identity.identity_engine()

    def testRandom(self):
        seed = 1

        h1 = self.eng.Run(self.w1,self.d.payload,self.epsilon,seed)
        h2 = self.eng.Run(self.w1,self.d.payload,self.epsilon,seed)
        self.assertSequenceEqual(list(h1),list(h2))

        numpy.random.seed(100)#see if setting numpy seed would affect random state object prng


        h3 = self.eng.Run(self.w1,self.d.payload,self.epsilon,seed)
        self.assertSequenceEqual(list(h1),list(h3))

    def testRandom2(self):
        seed = 1


        self.loadD = dataset.DatasetSampledFromFile(nickname='ADULTFRANK', sample_to_scale=1000, reduce_to_dom_shape = (32,32),  seed=111)
        h1 = self.eng.Run(self.w2,self.loadD.payload,self.epsilon,seed)
        h2 = self.eng.Run(self.w2,self.loadD.payload,self.epsilon,seed)
        self.assertSequenceEqual(list(h1),list(h2))

        numpy.random.seed(100)#see if setting numpy seed would affect random state object prng

        h3 = self.eng.Run(self.w2,self.loadD.payload,self.epsilon,seed)
        self.assertSequenceEqual(list(h1),list(h3))

if __name__ == "__main__":
    unittest.main(verbosity=2)   
