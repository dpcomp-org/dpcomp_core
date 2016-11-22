from Kd_standard import Kd_standard
from Params import Params

class Kd_noisymean(Kd_standard):
    """ similar to Kd-standard, except that noisy mean is used as the split point
    we only use leaves to answer queries in this case """
    def __init__(self, data, param):
        Kd_standard.__init__(self, data, param)
    
    def getCountBudget(self):
        count_eps = self.param.Eps*(1-self.param.Percent)
        H = Params.maxHeight
        ret = [0 for i in range(H)]
        ret.append(count_eps)
        return ret    
    