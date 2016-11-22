import numpy as np
from Kd_true import Kd_true
from Params import Params
import sys
import logging

class Kd_standard(Kd_true):
    """ standard private kd-tree """
    def __init__(self, data, param):
        Kd_true.__init__(self, data, param)
    
    def getCountBudget(self):
        count_eps = self.param.Eps*(1-self.param.Percent)
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
            
    def getSplitBudget(self):
        split_eps = self.param.Eps*self.param.Percent
        H = Params.maxHeight
        return [split_eps/H for i in range(H)]
    
    def getNoisyMedian(self, array, left, right, epsilon):
        if self.param.splitScheme == 'expo':
            return self.differ.getSplit_exp(array, left, right, epsilon)
        elif self.param.splitScheme == 'noisyMean':
            return self.differ.getSplit_noisyMean(array, left, right, epsilon)
        else:
            logging.error('No such split scheme')
            sys.exit(1)