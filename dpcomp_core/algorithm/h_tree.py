from __future__ import division
######################################################################
#  Computing the MinL2 solution for a hierarchical tree of queries
#
#  The HTree class is a hierarchical tree that can be used to store true counts,
#  noisy counts, and inferred counts.  Initialize an HTree by passing in an arity
#  and true counts for the leaves (from which the other counts are automatically
#  computed).  User must assign noisy counts to each node.  The inference method
#  infers consistent counts from the noisy ones.
#
#  Output: a consistent estimate for the leaf counts.
#
#  The original theoretical justification for this algorithm was presented in:
#
#  Boosting the Accuracy of Differentially-Private Histograms Through Consistency
#  Michael Hay and Vibhor Rastogi and Gerome Miklau and Dan Suciu
#  International Conference on Very Large Data Bases (VLDB) 2010
#  Preprint, arXiv:0904.0942 2009
#
#  Examples:
#
#	>>> import h_tree
#	>>> tree = h_tree.HTree(2, [0]*2)
#	>>> [parent, child1, child2] = tree.preorder_iter()
#	>>> parent.noisy = 0
#	>>> child1.noisy = child2.noisy = 0.5
#	>>> leaves = tree.inference()
#	>>> print leaves
#	[0.16666666666666663, 0.16666666666666663]
#	>>> print tree
#	HNode(start: 0, end: 0) = (count=0, noisy=0.5, inferred=0.166666666667)
#	HNode(start: 1, end: 1) = (count=0, noisy=0.5, inferred=0.166666666667)
#	HNode(start: 0, end: 1) = (count=0, noisy=0, inferred=0.333333333333)
#

from builtins import map
from builtins import range
from builtins import object
import math
from functools import reduce
from dpcomp_core import util

class HNode(object):
	def __init__(self, start, end, count):
		self.start = start
		self.end = end
		self.count = count
		self.noisy = None
		self.hbar = None
		self.parent = None
		self.children = []
	def isleaf(self):
		return len(self.children) == 0
	def __repr__(self):
		return 'HNode(start: %d, end: %d) = (count=%s, noisy=%s, inferred=%s)' % (self.start, self.end, self.count, self.noisy, self.hbar)
		
class HTree(object):
	"Complete k-ary tree for H query"
	def __init__(self, arity, leaf_counts):
		self.k = arity
		height = int(math.ceil(math.log(len(leaf_counts), arity))) + 1
		assert arity**(height-1) == len(leaf_counts), \
		'Invalid number of leaves, %d, must be power of %d' % (len(leaf_counts), arity)
		
		# build a complete tree of arity k
		nodes = []
		for i in range(len(leaf_counts)):
			nodes.append( HNode(i, i, leaf_counts[i]) )
			
		while len(nodes) > 1:
			siblings = nodes[:self.k]
			del nodes[:self.k]
			total = reduce(lambda x,y: x + y.count, siblings, 0)  # sum up counts of siblings
			start = siblings[0].start
			end = siblings[-1].end
			parent = HNode(start, end, total)
			for node in siblings:
				self.__add_child(parent, node)
			nodes.append( parent )
		
		self.root = nodes[0]
		self.height = height
			
	def __repr__(self):
		return '\n'.join([x.__repr__() for x in self.postorder_iter()])

	def inference(self):
		k = self.k
		# go bottom up to compute z[v]
		for (node, h) in self.postorder_iter(with_height=True):
			if node.isleaf():
				node.hbar = node.noisy
			else:
				alpha = k**(h-1)
				a = ((k-1)*alpha) * node.noisy
				total = reduce(lambda total,child: total + child.hbar, node.children, 0)
				node.total_z_children = total
				b = (alpha - 1) * total
				node.hbar = util.old_div(float(a + b), (k*alpha - 1))

		# go top down to compute hbar[v]
		leaves = [None]*(k**(self.height-1))
		for node in self.preorder_iter():
			if node == self.root:
				continue
			parent = node.parent
			sum_z = parent.total_z_children
			node.hbar += util.old_div((parent.hbar - sum_z),k)
			if node.isleaf():
				assert leaves[node.start] == None
				leaves[node.start] = node.hbar
		
		# check that all leaves are filled in
		assert reduce(lambda total,leaf_count: (leaf_count==None) + total, leaves, 0) == 0
		return leaves
			
	def postorder_iter(self, with_height=False):
		stack = [(self.root, 0, self.height)]
		while stack:
			(node, num_pops, height) = stack.pop()
			if node.isleaf() or num_pops == self.k:
				if with_height:
					yield (node, height)
				else:
					yield node
			else:
				stack.append( (node, num_pops+1, height) )
				stack.append( (node.children[num_pops], 0, height-1) )

	def preorder_iter(self, with_height=False):
		stack = [(self.root, self.height)]
		while stack:
			(node, height) = stack.pop()
			if with_height:
				yield (node, height)
			else:
				yield node
			list(map(lambda child: stack.append((child, height-1)), node.children))

	def __add_child(self, parent, node):
		parent.children.append(node)
		node.parent = parent



import unittest
class Test(unittest.TestCase):

	def test_inference1(self):
		htree = HTree(2, [0]*2)
		[parent, child1, child2] = htree.preorder_iter()
		parent.noisy = 0
		child1.noisy = 0.5
		child2.noisy = 0.5
		leaves = htree.inference()
		self.assertEqual(2, len(leaves))
		self.assertAlmostEqual(util.old_div(1.,6), leaves[0])
		self.assertAlmostEqual(util.old_div(1.,6), leaves[1])

	def test_inference2(self):
		htree = HTree(2, [0]*2)
		[parent, child1, child2] = htree.preorder_iter()
		parent.noisy = 0
		child1.noisy = 1
		child2.noisy = 0
		leaves = htree.inference()
		self.assertEqual(2, len(leaves))
		self.assertAlmostEqual(util.old_div(-1.,3), leaves[0])
		self.assertAlmostEqual(util.old_div(2.,3), leaves[1])

	def test_inference3(self):
		htree = HTree(2, [0]*2)
		[parent, child1, child2] = htree.preorder_iter()
		parent.noisy = 0
		child1.noisy = 1
		child2.noisy = 0
		leaves = htree.inference()
		self.assertEqual(2, len(leaves))
		self.assertAlmostEqual(util.old_div(-1.,3), leaves[0])
		self.assertAlmostEqual(util.old_div(2.,3), leaves[1])


if __name__ == '__main__':
	 unittest.main()
