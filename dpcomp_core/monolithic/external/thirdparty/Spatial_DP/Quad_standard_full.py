from Quad_standard import Quad_standard
from Params import Params

class Quad_standard_full(Quad_standard):
    """ Grow a full balanced tree, ignore the minPartSize stopping condition"""
    def __init__(self, data, param):
        Quad_standard.__init__(self, data, param)
        
    def testLeaf(self, curr):
        if (curr.n_depth == Params.maxHeight) or (curr.n_budget <= 0):
            return True
        return False
