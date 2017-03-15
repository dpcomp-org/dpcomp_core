import os
import unittest
from dpcomp_core import util

try:
    LOG_PATH = os.environ['DPCOMP_LOG_PATH']
except KeyError as e:
    raise RuntimeError("DPCOMP_LOG_PATH environment variable not set.")

try:
    LOG_LEVEL = os.environ['DPCOMP_LOG_LEVEL']
except KeyError as e:
    raise RuntimeError("DPCOMP_LOG_LEVEL environment variable not set.")

class TestCommon(unittest.TestCase):

    def setUp(self):
        util.setup_logging('dpcomp', os.path.join(LOG_PATH, 'test.out'), LOG_LEVEL)

        self.maxDiff = None

    def tearDown(self):
        pass
