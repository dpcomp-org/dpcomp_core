import numpy
from dpcomp_core.workload import *
import unittest


class WorkloadTests(unittest.TestCase):

    def setUp(self):
        self.n_sqrt = 32
        self.oneD = (self.n_sqrt * self.n_sqrt,)
        self.oneDint = self.oneD[0]
        self.twoD = (self.n_sqrt,self.n_sqrt)

        self.x_range = numpy.array( range(self.n_sqrt * self.n_sqrt) )
        self.x_ones = numpy.ones_like(self.x_range)
        self.x_zeros = numpy.zeros_like(self.x_range)

        self.X = [self.x_zeros, self.x_ones, self.x_range]

    def testIdentity(self):

        W1 = Identity(self.oneD, weight=1.0)
        W11 = Identity.oneD(self.oneDint, weight=1.0)
        W2 = Identity(self.twoD, weight=1.0)

        self.assertEquals(W1.sensitivity(), 1.0)
        self.assertEquals(W1.sensitivity_from_matrix(), 1.0)

        self.assertEquals(W11.sensitivity(), 1.0)
        self.assertEquals(W11.sensitivity_from_matrix(), 1.0)

        self.assertEquals(W2.sensitivity(), 1.0)
        self.assertEquals(W2.sensitivity_from_matrix(), 1.0)

        for x in self.X:
            res = W1.evaluate(x)
            self.assertTrue( numpy.all(res==x))

        for x in self.X:
            res = W11.evaluate(x)
            self.assertTrue( numpy.all(res==x))

        for x in self.X:
            res = W2.evaluate(x)
            self.assertTrue( numpy.all(res.reshape(self.twoD) == x.reshape(self.twoD)))

        self.assertEquals(W1.hash, W11.hash)
        self.assertNotEqual(W1.hash, W2.hash)

    def testPrefix1D(self):

        P = Prefix1D(self.oneDint)
        PP = eval( P.__repr__() )
        self.assertEqual(P.hash, PP.hash)



if __name__ == "__main__":
    unittest.main(verbosity=2)
