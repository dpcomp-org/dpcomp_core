from builtins import str
from dpcomp_core.mixins import Cacheable
import hashlib
import math
import numpy
from dpcomp_core.mixins import Marshallable
import time
from dpcomp_core import util
from dpcomp_core import metric


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

        # algorithm algorithms return only X_hat (a numpy.ndarray)
        # alg-op operator algorithms returns the tuple (X_hat, ancillary_output) 
        ret = self.maybe(self.A, X_hat_key,'Run', (self.W, self.X.payload, self.epsilon, self.seed))

        if isinstance(ret, numpy.ndarray):
            self.X_hat = ret
        else:
            self.X_hat, self.ancillary_output = ret

        self.time = time.time() - start

        return self

    @property
    def key(self):
        return self.hash[:24]

    @property
    def hash(self):
        m = hashlib.sha1()

        m.update(util.prepare_for_hash(self.__class__.__name__))
        m.update(util.prepare_for_hash(str(self.epsilon)))
        m.update(util.prepare_for_hash(str(self.seed)))
        m.update(util.prepare_for_hash(self.X.hash))
        m.update(util.prepare_for_hash(self.W.hash))
        m.update(util.prepare_for_hash(self.A.hash))

        return m.hexdigest()

    def analysis_payload(self):
        return util.class_to_dict(self, ignore_list=['A', 'M', 'W', 'X', 'X_hat', 'init_params', '_cache'])

    def asDict(self):
        return util.class_to_dict(self)
