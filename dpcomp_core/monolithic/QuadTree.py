import numpy 
import math
from dpcomp_core.monolithic import estimate_engine
from dpcomp_core import util

from dpcomp_core.monolithic.external.thirdparty.Spatial_DP.Params import Params
from dpcomp_core.monolithic.external.thirdparty.Spatial_DP.KExp import KExp


class QuadTree_engine(estimate_engine.estimate_engine):
    """ Estimate a 2D dataset by using QuadTree. """

    def __init__(self,c=10,short_name = "QuadTree"):
        #c is a parameter controlling the height of tree
        self.init_params = util.init_params_from_locals(locals())
        self.c = c
        self.short_name = short_name

    def Run(self,Q,x,epsilon,seed):
        assert seed is not None, 'seed must be set'

        prng = numpy.random.RandomState(seed)

        assert len(x.shape)==2, '%s is defined for 2D data only' % self.__class__.__name__

        l1,l2 = x.shape
    
        querylist = []
        for i in range(l1):
            for j in range(l2):
                querylist.append(numpy.array([[i-0.5,j-0.5],[i+0.5,j+0.5]]))


        X = [[],[]];
        for i in range(l1):
            for j in range(l2):
                if x[i][j] != 0:
                    X[0] = X[0] + [i]*x[i][j]
                    X[1] = X[1] + [j]*x[i][j]
        Y = numpy.ndarray((2,len(X[0])),'float32')
        for i in range(2):
            Y[i] = X[i]


        # parameter c = 10
        Params.maxHeight = self.c
        if int(math.log(l1)) < self.c:
            Params.maxHeight = int(math.ceil(math.log(l1)))

        Params.NDIM, Params.NDATA = Y.shape
        Params.LOW, Params.HIGH = numpy.amin(Y,axis=1), numpy.amax(Y,axis=1)



        kexp = KExp(Y,querylist)

        p = Params(prng)
        p.Eps = epsilon
        tmp = kexp.run_Quad_opt(p)

        result = numpy.ndarray((l1,l2),'float32')
        for i in range(l1):
            result[i] = tmp[i*l2:i*l2 + l2]
        return result




