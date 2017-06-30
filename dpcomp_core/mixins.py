from builtins import object
from collections import defaultdict
from dpcomp_core import util


class Cache(object):

    def __init__(self):
        self._cache = defaultdict(dict)

    def is_present(self, label, key):
        return key in self._cache[label]

    def set(self, label, key, value):
        self._cache[label][key] = value

        return value

    def get(self, label, key):
        return self._cache[label][key]


class Cacheable(object):

    _cache = Cache()

    def maybe(self, obj, key, method_name, args=[]):
        """Returns the result of method_name applied to obj.
           The result is retreived from the cache if it exists,
           otherwise method_name is applied to obj on the spot.
        """
        label = self.__label_for(obj)

        if self._cache.is_present(label, key):
            _obj = self._cache.get(label, key)
        else:
            _obj = getattr(obj, method_name)(*args)
            self._cache.set(label, key, _obj)

        return _obj

    def get_if_set(self, obj, key, method_name, args=[]):
        """Returns the result of method_name applied to obj provided
           it exists in cache. Otherwise it returns None.
        """
        label = self.__label_for(obj)

        if self.is_set(obj, key):
            return self._cache.get(label, key)
        else:
            return obj

    def is_set(self, obj, key):
        label = self.__label_for(obj)

        return self._cache.is_present(label, key)

    def __label_for(self, obj):
        return obj.__class__.__name__

    @staticmethod
    def reset():
        Cacheable._cache = Cache()


class Marshallable(object):

    def marshal(self):
        return {'marshaled': True,
                'class': util.classname(self),
                'init_params': util.prepare_for_json(self.init_params)}

    @classmethod
    def unmarshal(cls, marshaled):
        return cls(**util.receive_from_json(marshaled))


class Inspectable(object):
    """Objects that inherit from this class should ensure that
       every instance member has a type that can be handled by
       dpcomp_core.util.prepare_for_json.
    """

    def inspect(self):
        return vars(self)
