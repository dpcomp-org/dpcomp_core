from dpcomp_core.mixins import Marshallable
from dpcomp_core import util
import hashlib

import AG
import ahp
import DPcube1D
import DPcube
import dawa
import estimate_engine
import HB
import HB2D
import identity
import QuadTree
import mwemND
import privelet
import privelet2D
import QuadTree
import thirdparty
import UG
import uniform


class BaseAlgorithm(Marshallable):

    def __init__(self):
        raise NotImplementedError()

    def Run(self, Q, x, epsilon, seed=None):
        raise NotImplementedError()

    def asDict(self):
        d = util.class_to_dict(self)
        return d

    def analysis_payload(self):
        return util.class_to_dict(self)

    @property
    def key(self):
        """ Using leading 8 characters of hash as key for now """
        return self.hash[:8]


    @property
    def hash(self):
        """
        Uniqueness of this hash relies on subclasses writing init parameters as instance variables
        """
        m = hashlib.sha1()
        m.update(self.__class__.__name__)
        m.update(str(util.standardize(sorted(self.init_params.items()))))
        return m.hexdigest()
