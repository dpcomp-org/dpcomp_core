import math
import numpy as np
from dpcomp_core.monolithic.ahp import ahp_engine
from dpcomp_core.monolithic import estimate_engine
from dpcomp_core import util 


""" Wrapper to support n-dimensional data using original AHP implementation
"""

class ahpND_engine(estimate_engine.estimate_engine):
    
    def __init__(self, ratio=0.85, eta=0.35, short_name = 'AHP'):
        self.init_params = util.init_params_from_locals(locals())
        self._ratio = ratio
        self._eta = eta 
        self.short_name = short_name

    
    def Run(self, Q, x, epsilon, seed):
        assert seed is not None, 'seed must be set'

        engine = ahp_engine(self._ratio, self._eta)
        shape = x.shape
        hatx1d = engine.Run(Q, np.reshape(x, x.size), epsilon, seed)  # call AHP on 1d array
        hatx1d = np.array(hatx1d) # might come back as a list
        return np.reshape(hatx1d, shape)



class ahpND_adaptive_engine(estimate_engine.estimate_engine):
    """Adaptive version assumes true scale known"""
    
    def __init__(self, index = 'DEFAULT1D', short_name = 'AHP*'):
        self.init_params = util.init_params_from_locals(locals())

        self._vSEP = Lfunction[index]['vSEP']
        self._vRatio = Lfunction[index]['vRatio']
        self._vEta = Lfunction[index]['vEta']
        self.short_name = short_name
    

    def Run(self, Q, x, epsilon, seed):

        #split part of the privacy budget to calculate SEP and select parameters
        assert seed is not None, 'seed must be set'
        
        Ntotal = x.sum() 

        SEP =  Ntotal * epsilon
        self._ratio = float(np.interp(SEP,self._vSEP ,self._vRatio))
        self._eta = float(np.interp(SEP,self._vSEP ,self._vEta))

        ahp_nd_engine = ahpND_engine(self._ratio, self._eta)
    
        return ahp_nd_engine.Run(Q, x, epsilon, seed)

        
Lfunction ={ \
            #1D
            #POWER1
            'DEFALUT1D':{\
                'vSEP':[0, 50.0, 100.0,500.0,1000.0,10000.0,500000.0,1000000.0,5000000.0,10000000.0,100000000.0,1e+20],
                'vRatio':[0.7, 0.7, 0.7, 0.9, 0.9, 0.8, 0.7, 0.5, 0.5, 0.3, 0.3, 0.3],
                'vEta':[0.2, 0.2, 0.1, 0.2, 0.1, 0.1, 0.3, 0.1, 0.2, 0.1, 0.3, 0.3]},
            #2D
            #TDNORMAL1
            'DEFALUT2D':{\
                'vSEP':[0,500.0,1000.0,5000.0,10000.0,100000.0,500000.0,1000000.0,5000000.0,10000000.0,100000000.0,1e+20],
                'vRatio':[0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.7, 0.5, 0.7, 0.5, 0.5],
                'vEta':[0.5, 0.5, 0.1, 0.1, 0.1, 0.3, 0.7, 0.1, 0.1, 0.9, 0.1, 0.1]},
        
}
