"""Classes of partition engines."""


from builtins import object
class partition_engine(object):
	"""The template class for partition engines."""

	@staticmethod
	def Run(x, epsilon, ratio):
		"""Run templated for partition engine.

		x - the input dataset
		epsilon - the total privacy budget
		ratio - the ratio of privacy budget used for partitioning.
		"""
		raise NotImplementedError('A Run method must be implemented'
								  ' for a partition engine.')


