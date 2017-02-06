from dpcomp_core import experiment
from dpcomp_core import dataset
from dpcomp_core import metric
from dpcomp_core import workload
from dpcomp_core.algorithm import uniform, AG
from test import TestCommon
import unittest


class TestExperiment(TestCommon):

    def setUp(self):
        super(TestExperiment, self).setUp()

        domain1 = 1024
        sample = 1E4
        domain2 = (32,32)   # numpy shape tuple

        self.expr_seed = 12345
        self.expr_eps = 0.1

        # 1D data and workload
        self.X1 = dataset.DatasetSampledFromFile(nickname='HEPTH', sample_to_scale=sample, reduce_to_dom_shape=domain1, seed=111)
        self.W1 = workload.Prefix1D(domain_shape_int=domain1)

        # 2D data and workload
        self.X2 = dataset.DatasetSampledFromFile(nickname='SF-CABS-S', sample_to_scale=sample, reduce_to_dom_shape = domain2, seed=111)
        self.W2 = workload.RandomRange(shape_list=[(5,5),(10,10)], domain_shape=domain2, size=1000, seed=9001)

        self.A = uniform.uniform_noisy_engine()     # this algorithm works for 1D and 2D
        self.A2 = AG.AG_engine(c=10, c2=5, alpha=.4)      # this algorithm works for 2D only

    def tearDown(self):
        super(TestExperiment, self).tearDown()

    def test_X_can_marshal(self):
        self.assertEqual(type(self.X1.asDict()), dict)
        self.assertEqual(type(self.X2.asDict()), dict)

    def test_W_can_marshal(self):
        self.assertEqual(type(self.W1.asDict()), dict)
        self.assertEqual(type(self.W2.asDict()), dict)

    def test_A_can_marshal(self):
        self.assertEqual(type(self.A.asDict()), dict)
        self.assertEqual(type(self.A2.asDict()), dict)

    def test_experiment_can_run(self):
        E = experiment.Single(self.X1, 
                              self.W1, 
                              self.A, 
                              epsilon=self.expr_eps, 
                              seed=self.expr_seed).run()

        E_dict = E.asDict()
        self.assertEqual(self.expr_seed, E_dict['seed'])
        self.assertEqual(self.expr_eps, E_dict['epsilon'])
if __name__ == "__main__":
    unittest.main(verbosity=3)
