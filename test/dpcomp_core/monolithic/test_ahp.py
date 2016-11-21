"""Unit test for ahp.py"""

import numpy
from dpcomp_core.monolithic import ahp
from dpcomp_core.mechanism import workload 
from dpcomp_core.mechanism import dataset
import unittest

class AHPTests(unittest.TestCase):


    def setUp(self):
        n = 1024
        self.hist = numpy.array( range(n))
        self.d = dataset.Dataset(self.hist, None)
    
        self.epsilon = 0.1
        self.w1 = workload.Identity.oneD(1024 , weight = 1.0)
        self.w2 = workload.Prefix1D(1024)
        self.eng = ahp.ahp_engine(ratio = 0.5, eta = 0.4)

    def testRandom(self):
        seed = 1

        h1 = self.eng.Run(self.w1,self.d.payload,self.epsilon,seed)
        h2 = self.eng.Run(self.w1,self.d.payload,self.epsilon,seed)
        self.assertSequenceEqual(list(h1),list(h2))

        numpy.random.seed(100)#see if setting numpy seed would affect random state object prng


        h3 = self.eng.Run(self.w1,self.d.payload,self.epsilon,seed)
        self.assertSequenceEqual(list(h1),list(h3))


if __name__ == "__main__":
    unittest.main(verbosity=2)   
