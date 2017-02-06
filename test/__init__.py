import os
import unittest
from dpcomp_core import util

LOG_PATH = os.environ['DPCOMP_LOG_PATH']
LOG_LEVEL = os.environ['DPCOMP_LOG_LEVEL']


class TestCommon(unittest.TestCase):

    def setUp(self):
        util.setup_logging('dpcomp', os.path.join(LOG_PATH, 'test.out'), LOG_LEVEL)

        self.maxDiff = None

    def tearDown(self):
        pass
