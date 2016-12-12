from dpcomp_core.harness import experiment
from dpcomp_core.mechanism import dataset
from dpcomp_core.mechanism import metric
from dpcomp_core.mechanism import workload
from dpcomp_core.monolithic import uniform, AG_noisy
from test import TestCommon
import unittest


class TestExecution(TestCommon):

    def setUp(self):
        super(TestExecution, self).setUp()

        domain1 = 1024
        sample = 1E4
        domain2 = (32,32) 

        self.expr_seed = 12345
        self.expr_eps = 0.1

        self.X1 = dataset.DatasetSampledFromFile(nickname='HEPTH', sample_to_scale=sample, reduce_to_dom_shape=domain1, seed=111)
        self.W1 = workload.Prefix1D(domain_shape_int=domain1)

        self.X2 = dataset.DatasetSampledFromFile(nickname='SF-CABS-S', sample_to_scale=sample, reduce_to_dom_shape = domain2, seed=111)
        self.W2 = workload.RandomRange(shape_list=[(5,5),(10,10)], domain_shape=domain2, size=1000, seed=9001)

        self.A1 = uniform.uniform_noisy_engine()
        self.A2 = AG_noisy.AG_engine_Noisy(c=10, c2=5, alpha=.4, totalBudget=.02)

        self.E1 = experiment.Single(self.X1, 
                                    self.W1, 
                                    self.A1, 
                                    epsilon=self.expr_eps, 
                                    seed=self.expr_seed)
        self.E2 = experiment.Single(self.X2, 
                                    self.W2, 
                                    self.A2, 
                                    epsilon=self.expr_eps, 
                                    seed=self.expr_seed)

        self.M1 = metric.SampleError(self.E1)
        self.M2 = metric.PopulationError(self.E2)


    def tearDown(self):
        super(TestExecution, self).tearDown()

    def test_metric_execution(self):
        self.M1.compute()
        self.assertEqual('error_payload' in self.M1.analysis_payload(), True)

        self.M2.compute()
        self.assertEqual('error_payload' in self.M2.analysis_payload(), True)