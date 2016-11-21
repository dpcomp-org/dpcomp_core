''' Measurement classes '''
import numpy
from dpcomp_core import helper

class MeasureLaplace(object):
	''' Laplace mechanism; return list of noisy query answers '''

	def go(self, x, Queries, local_eps):
		return helper.LaplaceMechParallel(x, Queries, local_eps)	# move this fcn from helper to this class?

