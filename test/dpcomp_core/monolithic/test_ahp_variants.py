from dpcomp_core.harness import experiment
from dpcomp_core.mechanism import dataset
from dpcomp_core.mechanism import metric
from dpcomp_core.mechanism import workload
from dpcomp_core.monolithic import *

from test import TestCommon
import unittest
import numpy 


''' Temporary tests for variants of AHP which tries to speed up the execution

'''
class TestAlgorithm(TestCommon):

    def setUp(self):
        super(TestAlgorithm, self).setUp()

        domain1 = 1024
        sample = 1E4
        domain2 = (32,32)   # numpy shape tuple

        self.expr_seed1 = 12345
        self.expr_seed2 = 12346

        self.expr_eps1 = 0.1
        self.expr_eps2 = 1

        # 1D data and workload
        self.X1 = dataset.DatasetSampledFromFile(nickname='ADULTFRANK', sample_to_scale=sample, reduce_to_dom_shape=domain1, seed=111)
        self.W1 = workload.Prefix1D(domain_shape_int=domain1)

        # 2D data and workload
        self.X2 = dataset.DatasetSampledFromFile(nickname='SF-CABS-E', sample_to_scale=sample, reduce_to_dom_shape = domain2, seed=111)
        self.W2 = workload.RandomRange(shape_list=[(5,5),(10,10)], domain_shape=domain2, size=1000, seed=9001)

        self.A = A = ahpND.ahpND_engine()
        self.A_fast = ahpND.ahpND_fast_engine()


    def test_equivelance(self):
        """Check equivalence of the optimized cython version and original implementation."""
        res1 = self.A.Run(self.W1, self.X1.payload, self.expr_eps1, self.expr_seed1)
        res2 = self.A_fast.Run(self.W1, self.X1.payload, self.expr_eps1, self.expr_seed1)
        numpy.testing.assert_array_equal(res1,res2)
    
        res3 = self.A.Run(self.W2, self.X2.payload, self.expr_eps1, self.expr_seed1)
        res4 = self.A_fast.Run(self.W2, self.X2.payload, self.expr_eps1, self.expr_seed1)
        numpy.testing.assert_array_equal(res3,res4)

        res5 = self.A.Run(self.W1, self.X1.payload, self.expr_eps2, self.expr_seed2)
        res6 = self.A_fast.Run(self.W1, self.X1.payload, self.expr_eps2, self.expr_seed2)
        numpy.testing.assert_array_equal(res5,res6)
    
        res5 = self.A.Run(self.W2, self.X2.payload, self.expr_eps2, self.expr_seed2)
        res6 = self.A_fast.Run(self.W2, self.X2.payload, self.expr_eps2, self.expr_seed2)
        numpy.testing.assert_array_equal(res5,res6)
if __name__ == "__main__":
    unittest.main(verbosity=2)
