from dpcomp_core.mixins import Marshallable
from dpcomp_core.monolithic import uniform
from dpcomp_core.monolithic import identity
from dpcomp_core.monolithic import UG
from dpcomp_core.monolithic import UG_noisy
from dpcomp_core.monolithic import AG
from dpcomp_core.monolithic import AG_noisy
from dpcomp_core.monolithic import HB
from dpcomp_core.monolithic import HB2D
from dpcomp_core.monolithic import ahp
from dpcomp_core.monolithic import ahpND
from dpcomp_core.monolithic import QuadTree
from dpcomp_core.monolithic import MyQuadTree
from dpcomp_core.monolithic import HybridTree
from dpcomp_core.monolithic import privelet
from dpcomp_core.monolithic import privelet2D
from dpcomp_core.monolithic import DPcube1D
from dpcomp_core.monolithic import DPcube
from dpcomp_core.monolithic import mwemND
from dpcomp_core.monolithic import greedyH
from dpcomp_core.monolithic import greedyH_only
from dpcomp_core.monolithic import dawa
from dpcomp_core.monolithic import dawa2D
from dpcomp_core.monolithic import thirdParty

from dpcomp_core import util
import hashlib


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

    # TODO: (check)
    @property
    def hash(self):
        """
        Uniqueness of this hash relies on subclasses writing init parameters as instance variables
        """
        m = hashlib.sha1()
        m.update(self.__class__.__name__)
        m.update(str(util.standardize(sorted(self.init_params.items()))))
        return m.hexdigest()
