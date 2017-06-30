from __future__ import absolute_import
from builtins import str
from dpcomp_core.mixins import Marshallable
from dpcomp_core import util
import hashlib

from . import AG
from . import ahp
from . import DPcube1D
from . import DPcube
from . import dawa
from . import estimate_engine
from . import HB
from . import HB2D
from . import identity
from . import QuadTree
from . import mwemND
from . import privelet
from . import privelet2D
from . import QuadTree
from . import thirdparty
from . import UG
from . import uniform


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
        m.update(util.prepare_for_hash(self.__class__.__name__))
        m.update(util.prepare_for_hash(str(util.standardize(sorted(self.init_params.items())))))
        return m.hexdigest()
