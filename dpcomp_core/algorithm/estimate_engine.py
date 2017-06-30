from builtins import str
import hashlib
from dpcomp_core.mixins import Marshallable
from dpcomp_core import util

class estimate_engine(Marshallable):
    """The template class for query engine."""

    def Run(self, Q, x, epsilon, seed=None):
        """Return an estimate dataset of x
        to answer Q with privacy budget epsilon.

        Q - the query workload
        x - the underlying dataset.
        epsilon - privacy budget.
        seed - seed for pseudo-random number generator (numpy.random.RandomState)

        Generally speaking, the query engine can be any
        differentially privacy algorithm.
        """
        raise NotImplementedError('A Run method must be implemented'
                                  ' for a query engine.')
        pass

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
