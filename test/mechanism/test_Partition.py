"""Unit test for Partition class"""

import unittest
import numpy as np
from dpcomp_core.mechanism.Partition import *
from dpcomp_core.mechanism.query_nd_union import *



class PartitionTestCase(unittest.TestCase):

    def setUp(self):
        pass

    def test_canonical(self):
        '''test of canonical order '''
        x1 = np.array([3,4,1,1])
        p1 = Partition(x1)
        p1c = Partition(x1,canonical_order = True)

        x2 = np.array([3,4,1,1,0,1]) 
        p2 = Partition(x2)
        p2c = Partition(x2, canonical_order = True)

        self.assertEqual(p1.output_shape,p1c.output_shape)
        self.assertEqual(p2.output_shape,p2c.output_shape)
        np.testing.assert_array_equal(p1c.vector,np.array([0, 1, 2, 2]))
        np.testing.assert_array_equal(p2c.vector,np.array([0,1,2,2,3,2]))


    def test_compose(self):
        ''' Basic compose without canonical order
        '''
        x = np.arange(8)
        p1 = Partition(np.array([3,1,2,1,3,4,0,4]))
        p2 = Partition(np.array([5,5,10,1,10]))

        # test that composed partition computes the composition of the individual partitions
        comp = p1.compose(p2)
        x_reduce1 = comp.reduce_data(x)
        x_reduce2 = p2.reduce_data(p1.reduce_data(x))
        np.testing.assert_array_equal(x_reduce1, x_reduce2)

        # attempting to compose mis-matched partitions raises error
        p3 = Partition(np.array([5,5,1,10]))
        with self.assertRaises(AssertionError):
            p1.compose(p3)

        # composing with unit_groups returns partition equivalent to original
        p3 = partition_unit_groups(5)
        comp = p1.compose(p3)
        np.testing.assert_array_equal(comp.vector, p1.vector)

    def test_compose_con(self):
        ''' Compose with canonical order
        '''
        x = np.arange(8)
        p1 = Partition(np.array([3,1,2,1,3,4,0,4]),canonical_order=True)
        p2 = Partition(np.array([5,5,10,1,10]),canonical_order=True)

        comp= p1.compose(p2) 
        x_reduce1 = comp.reduce_data(x)
        x_reduce2 = p2.reduce_data(p1.reduce_data(x))

        np.testing.assert_array_equal(x_reduce1,x_reduce2)


    def test_deviation(self):
        ''' Deviation is correct
        '''
        p1 = partition_one_group(4)
        x1 = np.array([10,0,10,0])
        self.assertEqual(p1.deviation(x1), 20)

        x2 = np.array([5,5,5,5])
        self.assertEqual(p1.deviation(x2), 0)

        p2 = Partition(np.array([0,0,1,1]))
        self.assertEqual(p2.deviation(x1), 20)

        p2 = Partition(np.array([0,0,1,1]))
        self.assertEqual(p2.deviation(x1, epsilon2=.5), 24)

if __name__== '__main__':
    unittest.main(verbosity=2)
