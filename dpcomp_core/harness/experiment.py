from dpcomp_core.mixins import Cacheable
import hashlib
import math
import numpy
from dpcomp_core.mixins import Marshallable
import time
from dpcomp_core import util
from dpcomp_core.mechanism import metric


class Single(Marshallable, Cacheable):

    def __init__(self, X, W, A, epsilon, seed=None):
        self.init_params = util.init_params_from_locals(locals())

        self.X = X
        self.W = W
        self.A = A
        self.epsilon = epsilon
        self.seed = seed

        self.X_hat = None
        self.state_op_log = None

    def run(self, update_payload=False):
        start = time.time()
        
        self.X = self.maybe(self.X, self.X.hash, 'compile')
        self.W = self.maybe(self.W, self.W.hash, 'compile')

        X_hat_key = self.A.hash + self.X.hash + self.W.hash + repr(self.epsilon) + repr(self.seed)

        # monolithic algorithms return X_hat (an ndarray)
        # Run method of alg-op algorithms now returns (X_hat, op_log) so we can capture op_log
        # See operators.Operator.Run(..)
        # This is a hack to handle both:
        ret = self.maybe(self.A, X_hat_key,'Run', (self.W, self.X.payload, self.epsilon, self.seed))
        if isinstance(ret, numpy.ndarray):
            self.X_hat = ret
        else:
            self.X_hat = ret[0]
            self.state_op_log = ret[1]

        self.time = time.time() - start

        return self

    @property
    def key(self):
        return self.hash[:24]

    @property
    def hash(self):
        m = hashlib.sha1()

        m.update(self.__class__.__name__)
        m.update(str(self.epsilon))
        m.update(str(self.seed))
        m.update(self.X.hash)
        m.update(self.W.hash)
        m.update(self.A.hash)

        return m.hexdigest()

    def analysis_payload(self):
        return util.class_to_dict(self, ignore_list=['A', 'M', 'W', 'X', 'X_hat', 'init_params', '_cache'])

    def asDict(self):
        return util.class_to_dict(self)
