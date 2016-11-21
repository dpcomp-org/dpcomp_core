
"""Unit test for query_nd_union.py"""

import os, sys, time, numpy as np
sys.path.append('..')

from dpcomp_core.mechanism.query_nd_union import *
from dpcomp_core.mechanism.helper import *
import unittest
import numpy

class NDQueryUnionTests(unittest.TestCase):

	def testValidationDimensions(self):
		''' Inconsistent dimensions raises exception '''
		q = ndRangeUnion()
		self.assertRaises(AssertionError, q.add1DRange, (1,2), (3,), 1.0)
		self.assertRaises(AssertionError, q.addRange, (1,2), (3,4,5), 1.0)

	def testValidationLowerUpper(self):
		''' Lower must be less than upper '''
		q = ndRangeUnion()
		self.assertRaises(AssertionError, q.add1DRange, 3, 2, 4.0)
		self.assertRaises(AssertionError, q.addRange, (1,5), (5,4), 1.0)

	def testValidationDimensionsMultiRanges(self):
		''' Inconsistent dimensions of unioned ranges raises exception '''
		q = ndRangeUnion()
		q.addRange((1,2), (3,4), 1.0)
		self.assertRaises(AssertionError, q.addRange, (1,2,3), (3,4,5), 1.0)

	def testNDRangeUnionEval(self):
		''' ndRangeUnion query evaluation is correct.'''		
		y = numpy.ones(16).reshape(4,4)
		Q = ndRangeUnion()
		Q.addRange( (0,0), (1,1), 1.0 )	# 2 x 2 submatrix at top left
		Q.addRange( (2,2), (3,3), 2.0 ) # 2 x 2 submatrix at bottom right
		self.assertEqual( Q.eval(y), 4+4*2)
		z = numpy.arange(16).reshape(4,4)
		self.assertEqual( Q.eval(z), 10+50*2)

	def testNDRangeUnionEvalEquivalence(self):
		''' ndRangeUnion query evaluation is equivalent to array method. '''		
		z = numpy.arange(16).reshape(4,4)
		Q = ndRangeUnion()
		Q.addRange( (0,0), (1,1), 1.0 )
		Q.addRange( (2,2), (3,3), 2.0 )
		Qarray = Q.asArray(shape=z.shape)
		ans = numpy.multiply(Qarray, z).sum() # sum of componentwise multiply
		self.assertEqual( Q.eval(z), ans)

	def testValidateShape(self):
		''' Shape validation works.'''		
		Q = ndRangeUnion()
		Q.addRange( (0,0), (1,1), 1.0 )
		Q.addRange( (2,2), (3,3), 2.0 )
		self.assertRaises(AssertionError, Q._validateShape, (5,5,5))	# too many dimensions
		self.assertRaises(AssertionError, Q._validateShape, (3,3))		# domain too small

	def testSensitivity(self):
		''' Sensitivity is calculated correctly.'''		
		Q = ndRangeUnion()
		Q.addRange( (0,0), (1,1), 2.0 )
		self.assertEqual(sensitivity([Q]),2.0)
		Q.addRange( (2,2), (3,3), 3.0 )
		self.assertEqual(sensitivity([Q]),3.0)
		P = ndRangeUnion()
		P.addRange( (0,0), (3,3), 5.0 )
		self.assertEqual(sensitivity([Q,P]),8.0)


if __name__ == "__main__":
    unittest.main(verbosity=2)   
