from dpcomp_core.harness import experiment
from dpcomp_core.mechanism import dataset
from dpcomp_core.mechanism import metric
from dpcomp_core.mechanism import workload
from dpcomp_core.monolithic import *

from test import TestCommon
import unittest


class TestAlgorithm(TestCommon):

    def setUp(self):
        super(TestAlgorithm, self).setUp()

        domain1 = 1024
        sample = 1E4
        domain2 = (32,32)   # numpy shape tuple

        self.expr_seed = 12345
        self.expr_eps = 0.1

        # 1D data and workload
        self.X1 = dataset.DatasetSampledFromFile(nickname='BIDS-ALL', sample_to_scale=sample, reduce_to_dom_shape=domain1, seed=111)
        self.W1 = workload.Prefix1D(domain_shape_int=domain1)

        # 2D data and workload
        self.X2 = dataset.DatasetSampledFromFile(nickname='SF-CABS-E', sample_to_scale=sample, reduce_to_dom_shape = domain2, seed=111)
        self.W2 = workload.RandomRange(shape_list=[(5,5),(10,10)], domain_shape=domain2, size=1000, seed=9001)

    def test_uniform_noisy_1D(self):
        A = uniform.uniform_noisy_engine() 
        E = experiment.Single(self.X1, 
                              self.W1, 
                              A, 
                              epsilon=self.expr_eps, 
                              seed=self.expr_seed).run()

        E_dict = E.asDict()
        self.assertEqual(self.expr_seed, E_dict['seed'])
        self.assertEqual(self.expr_eps, E_dict['epsilon'])

    def test_uniform_noisy_2D(self):
        A = uniform.uniform_noisy_engine() 
        E = experiment.Single(self.X2, 
                              self.W2, 
                              A, 
                              self.expr_eps, 
                              seed=self.expr_seed).run()

        E_dict = E.asDict()
        self.assertEqual(self.expr_seed, E_dict['seed'])
        self.assertEqual(self.expr_eps, E_dict['epsilon'])


    
    def test_identity(self):
        A = identity.identity_engine()
        E = experiment.Single(self.X1, 
                              self.W1, 
                              A, 
                              epsilon=self.expr_eps, 
                              seed=self.expr_seed).run()

        E_dict = E.asDict()
        self.assertEqual(self.expr_seed, E_dict['seed'])
        self.assertEqual(self.expr_eps, E_dict['epsilon'])

    def test_UG(self):
        A = UG.UG_engine()
        E = experiment.Single(self.X2, 
                              self.W2, 
                              A, 
                              epsilon=self.expr_eps, 
                              seed=self.expr_seed).run()

        E_dict = E.asDict()
        self.assertEqual(self.expr_seed, E_dict['seed'])
        self.assertEqual(self.expr_eps, E_dict['epsilon'])

    def test_AG(self):
        A = AG.AG_engine()
        E = experiment.Single(self.X2, 
                              self.W2, 
                              A, 
                              epsilon=self.expr_eps, 
                              seed=self.expr_seed).run()

        E_dict = E.asDict()
        self.assertEqual(self.expr_seed, E_dict['seed'])
        self.assertEqual(self.expr_eps, E_dict['epsilon'])

    def test_HB(self):
        A = HB.HB_engine()
        E = experiment.Single(self.X1, 
                              self.W1, 
                              A, 
                              epsilon=self.expr_eps, 
                              seed=self.expr_seed).run()

        E_dict = E.asDict()
        self.assertEqual(self.expr_seed, E_dict['seed'])
        self.assertEqual(self.expr_eps, E_dict['epsilon'])

    def test_HB2D(self):
        A = HB2D.HB2D_engine()
        E = experiment.Single(self.X2, 
                              self.W2, 
                              A, 
                              epsilon=self.expr_eps, 
                              seed=self.expr_seed).run()

        E_dict = E.asDict()
        self.assertEqual(self.expr_seed, E_dict['seed'])
        self.assertEqual(self.expr_eps, E_dict['epsilon'])

    def test_ahpND_1D(self):
        A = ahp.ahpND_engine()
        E = experiment.Single(self.X1, 
                              self.W1, 
                              A, 
                              epsilon=self.expr_eps, 
                              seed=self.expr_seed).run()

        E_dict = E.asDict()
        self.assertEqual(self.expr_seed, E_dict['seed'])
        self.assertEqual(self.expr_eps, E_dict['epsilon'])
    
    def test_ahpND_2D(self):
        A = ahp.ahpND_engine()
        E = experiment.Single(self.X2, 
                              self.W2, 
                              A, 
                              epsilon=self.expr_eps, 
                              seed=self.expr_seed).run()

        E_dict = E.asDict()
        self.assertEqual(self.expr_seed, E_dict['seed'])
        self.assertEqual(self.expr_eps, E_dict['epsilon'])

    def test_QuadTree(self):
        A = QuadTree.QuadTree_engine()
        E = experiment.Single(self.X2, 
                              self.W2, 
                              A, 
                              epsilon=self.expr_eps, 
                              seed=self.expr_seed).run()

        E_dict = E.asDict()
        self.assertEqual(self.expr_seed, E_dict['seed'])
        self.assertEqual(self.expr_eps, E_dict['epsilon'])

    def test_QuadTree(self):
        A = QuadTree.QuadTree_engine()
        E = experiment.Single(self.X2, 
                              self.W2, 
                              A, 
                              epsilon=self.expr_eps, 
                              seed=self.expr_seed).run()

        E_dict = E.asDict()
        self.assertEqual(self.expr_seed, E_dict['seed'])
        self.assertEqual(self.expr_eps, E_dict['epsilon'])

    def test_HybridTree(self):
        A = HybridTree.HybridTree_engine()
        E = experiment.Single(self.X2, 
                              self.W2, 
                              A, 
                              epsilon=self.expr_eps, 
                              seed=self.expr_seed).run()

        E_dict = E.asDict()
        self.assertEqual(self.expr_seed, E_dict['seed'])
        self.assertEqual(self.expr_eps, E_dict['epsilon'])
    
    def test_HybridTree(self):
        A = HybridTree.HybridTree_engine()
        E = experiment.Single(self.X2, 
                              self.W2, 
                              A, 
                              epsilon=self.expr_eps, 
                              seed=self.expr_seed).run()

        E_dict = E.asDict()
        self.assertEqual(self.expr_seed, E_dict['seed'])
        self.assertEqual(self.expr_eps, E_dict['epsilon'])

    def test_privelet(self):
        A = privelet.privelet_engine()
        E = experiment.Single(self.X1, 
                              self.W1, 
                              A, 
                              epsilon=self.expr_eps, 
                              seed=self.expr_seed).run()

        E_dict = E.asDict()
        self.assertEqual(self.expr_seed, E_dict['seed'])
        self.assertEqual(self.expr_eps, E_dict['epsilon'])

    def test_privelet2D(self):
        A = privelet2D.privelet2D_engine()
        E = experiment.Single(self.X2, 
                              self.W2, 
                              A, 
                              epsilon=self.expr_eps, 
                              seed=self.expr_seed).run()

        E_dict = E.asDict()
        self.assertEqual(self.expr_seed, E_dict['seed'])
        self.assertEqual(self.expr_eps, E_dict['epsilon'])

    def test_DPcube1D(self):
        A = DPcube1D.DPcube1D_engine()
        E = experiment.Single(self.X1, 
                              self.W1, 
                              A, 
                              epsilon=self.expr_eps, 
                              seed=self.expr_seed).run()

        E_dict = E.asDict()
        self.assertEqual(self.expr_seed, E_dict['seed'])
        self.assertEqual(self.expr_eps, E_dict['epsilon'])

    def test_DPcube(self):
        A = DPcube.DPcube_engine()
        E = experiment.Single(self.X2, 
                              self.W2, 
                              A, 
                              epsilon=self.expr_eps, 
                              seed=self.expr_seed).run()

        E_dict = E.asDict()
        self.assertEqual(self.expr_seed, E_dict['seed'])
        self.assertEqual(self.expr_eps, E_dict['epsilon'])


#Workload aware algorithms



    def test_mwemND_1D(self):
        A = mwemND.mwemND_engine()
        E = experiment.Single(self.X1, 
                              self.W1, 
                              A, 
                              epsilon=self.expr_eps, 
                              seed=self.expr_seed).run()

        E_dict = E.asDict()
        self.assertEqual(self.expr_seed, E_dict['seed'])
        self.assertEqual(self.expr_eps, E_dict['epsilon'])

    def test_mwemND_2D(self):
        A = mwemND.mwemND_engine()
        E = experiment.Single(self.X2, 
                              self.W2, 
                              A, 
                              epsilon=self.expr_eps, 
                              seed=self.expr_seed).run()

        E_dict = E.asDict()
        self.assertEqual(self.expr_seed, E_dict['seed'])
        self.assertEqual(self.expr_eps, E_dict['epsilon'])

    # use greedyH only, no partition engine used.
    def test_greedyH(self):
        A = dawa.greedyH_only_engine()
        E = experiment.Single(self.X1, 
                              self.W1, 
                              A, 
                              epsilon=self.expr_eps, 
                              seed=self.expr_seed).run()

        E_dict = E.asDict()
        self.assertEqual(self.expr_seed, E_dict['seed'])
        self.assertEqual(self.expr_eps, E_dict['epsilon'])

    def test_dawa(self):
        A = dawa.dawa_engine()
        E = experiment.Single(self.X1, 
                              self.W1, 
                              A, 
                              epsilon=self.expr_eps, 
                              seed=self.expr_seed).run()

        E_dict = E.asDict()
        self.assertEqual(self.expr_seed, E_dict['seed'])
        self.assertEqual(self.expr_eps, E_dict['epsilon'])

    def test_dawa2D(self):
        A = dawa.dawa2D_engine()
        E = experiment.Single(self.X2, 
                              self.W2, 
                              A, 
                              epsilon=self.expr_eps, 
                              seed=self.expr_seed).run()

        E_dict = E.asDict()
        self.assertEqual(self.expr_seed, E_dict['seed'])
        self.assertEqual(self.expr_eps, E_dict['epsilon'])

#Third party algorithms

    def test_StructureFirst(self):
        A = thirdparty.StructureFirst_engine()
        E = experiment.Single(self.X1, 
                              self.W1, 
                              A, 
                              epsilon=self.expr_eps, 
                              seed=self.expr_seed).run()
        E_dict = E.asDict()
        self.assertEqual(self.expr_seed, E_dict['seed'])
        self.assertEqual(self.expr_eps, E_dict['epsilon'])    
    def test_EFPA(self):
        A = thirdparty.efpa_engine()
        E = experiment.Single(self.X1, 
                              self.W1, 
                              A, 
                              epsilon=self.expr_eps, 
                              seed=self.expr_seed).run()
        E_dict = E.asDict()
        self.assertEqual(self.expr_seed, E_dict['seed'])
        self.assertEqual(self.expr_eps, E_dict['epsilon'])    
    def test_PHP(self):
        A = thirdparty.php_engine()
        E = experiment.Single(self.X1, 
                              self.W1, 
                              A, 
                              epsilon=self.expr_eps, 
                              seed=self.expr_seed).run()
        E_dict = E.asDict()
        self.assertEqual(self.expr_seed, E_dict['seed'])
        self.assertEqual(self.expr_eps, E_dict['epsilon'])

#Adaptive version of algorithms

    def test_AHP_ADP_1D(self):
        A = ahp.ahpND_adaptive_engine(index = 'DEFALUT1D')
        E = experiment.Single(self.X1, 
                              self.W1, 
                              A, 
                              epsilon=self.expr_eps, 
                              seed=self.expr_seed).run()
        E_dict = E.asDict()
        self.assertEqual(self.expr_seed, E_dict['seed'])
        self.assertEqual(self.expr_eps, E_dict['epsilon'])
    
    def test_AHP_ADP_2D(self):
        A = ahp.ahpND_adaptive_engine(index = 'DEFALUT2D')
        E = experiment.Single(self.X2, 
                              self.W2, 
                              A, 
                              epsilon=self.expr_eps, 
                              seed=self.expr_seed).run()
        E_dict = E.asDict()
        self.assertEqual(self.expr_seed, E_dict['seed'])
        self.assertEqual(self.expr_eps, E_dict['epsilon'])    

    def test_MWEM_ADP_1D(self):
        A = mwemND.mwemND_adaptive_engine(index = 'DEFALUT1D')
        E = experiment.Single(self.X1, 
                              self.W1, 
                              A, 
                              epsilon=self.expr_eps, 
                              seed=self.expr_seed).run()
        E_dict = E.asDict()
        self.assertEqual(self.expr_seed, E_dict['seed'])
        self.assertEqual(self.expr_eps, E_dict['epsilon'])   

    def test_MWEM_ADP_2D(self):
        A = mwemND.mwemND_adaptive_engine(index = 'DEFALUT2D')
        E = experiment.Single(self.X2, 
                              self.W2, 
                              A, 
                              epsilon=self.expr_eps, 
                              seed=self.expr_seed).run()
        E_dict = E.asDict()
        self.assertEqual(self.expr_seed, E_dict['seed'])
        self.assertEqual(self.expr_eps, E_dict['epsilon']) 
if __name__ == "__main__":
    unittest.main(verbosity=3)