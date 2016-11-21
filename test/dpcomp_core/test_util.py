import json
from dpcomp_core.mechanism import dataset
import numpy as np
import unittest
from dpcomp_core import util


class TestUtil(unittest.TestCase):

    def setUp(self):
        self.D = dataset.DatasetSampledFromFile(nickname='HEPTH',
                                                sample_to_scale=1E4,
                                                reduce_to_dom_shape=1024,
                                                seed=111)

    def test_json_primitives(self):
        self.assertEqual(13, serde(13))
        self.assertEqual(True, serde(True))
        self.assertEqual(3.14, serde(3.14))
        self.assertEqual('test', serde('test')) 
        self.assertEqual(u'test', serde(u'test')) 
        self.assertEqual(util.standardize((3,2)), 
                         util.standardize(serde((3,2))))
        self.assertEqual(['a', 'b'], serde(['a', 'b']))
        self.assertEqual(None, serde(None))

    def test_json_numpy_array(self):
        self.assertEqual(util.standardize(np.ones((3,2))), 
                         util.standardize(serde(np.ones((3,2)))))

    def test_json_persistable(self):
        self.assertEqual(self.D.hash, serde(self.D).hash)

    def test_json_mixed(self):
        d = {'a': 13,
             5: 3.14,
             (1,2): np.ones((3,2))}

        self.assertEqual(util.standardize(d), util.standardize(serde(d)))
                          
    def test_json_hierarchical(self):
        d1 = {'a': self.D,
              'b': {'b1': self.D,
                    'b2': {'b21': self.D}}}

        self.assertEqual(d1['a'].hash, serde(d1)['a'].hash)
        self.assertEqual(d1['b']['b1'].hash, serde(d1)['b']['b1'].hash)
        self.assertEqual(d1['b']['b2']['b21'].hash, serde(d1)['b']['b2']['b21'].hash)

        d2 = {1: np.ones((3,2)),
              2: {21: np.ones((5,4)),
                  22: {221: np.ones((13,2))}}}

        self.assertEqual(util.standardize(d2), util.standardize(serde(d2)))

def serde(item):
    return util.receive_from_json(json.loads(json.dumps(util.prepare_for_json(item))))
