from Kd_standard import Kd_standard
from Params import Params

class Kd_hybrid(Kd_standard):
    """ Hybrid kd-tree, use private medians for the first h levels and (data-independent) 
    domain mid-points for the remaining levels as the split points. """
    
    def __init__(self, data, param):
        Kd_standard.__init__(self, data, param)
    
    def getSplitBudget(self):
        split_eps = self.param.Eps*self.param.Percent
        sw = self.param.switchLevel # switching level
        H = Params.maxHeight
        ret = [split_eps/sw for i in range(sw)]
        for i in range(sw,H):
            ret.append(0)
        return ret
    
    def getSplit(self,array,left,right,epsilon):
        """ If epsilon is zero, return middle point of lower/upper bound """
        if epsilon < 10**(-6):
            return (left+right)/2
        else:
            return self.getNoisyMedian(array, left, right, epsilon)
