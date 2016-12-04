import numpy as np
from Kd_pure import Kd_pure
from Params import Params
import sys
import logging

class Kd_true(Kd_pure):
    """ non-private kd-tree, use true medians to split but noisy counts """
    def __init__(self, data, param):
        Kd_pure.__init__(self, data, param)
    
    def getCountBudget(self):
        count_eps = self.param.Eps
        H = Params.maxHeight
        if self.param.geoBudget == 'none':
            return [count_eps/(H+1) for i in range(H+1)]
        elif self.param.geoBudget == 'aggressive':
            unit = count_eps/(2**(H+1)-1)
            return [unit*2**i for i in range(H+1)]
        elif self.param.geoBudget == 'quadratic':
            unit = count_eps * (np.sqrt(2)-1) / (2**(0.5*(H+1))-1)
            return [unit*2**(0.5*i) for i in range(H+1)]
        elif self.param.geoBudget == 'optimal':
            unit = count_eps * ((2**(1.0/3))-1) / (2**((1.0/3)*(H+1))-1)
            return [unit*2**((1.0/3)*i) for i in range(H+1)]
        elif self.param.geoBudget == 'quartic':
            unit = count_eps * ((2**(1.0/4))-1) / (2**((1.0/4)*(H+1))-1)
            return [unit*2**((1.0/4)*i) for i in range(H+1)]
        else:
            logging.error('No such geoBudget scheme')
            sys.exit(1)
        