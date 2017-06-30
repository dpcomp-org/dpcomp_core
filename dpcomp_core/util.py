from builtins import map
from builtins import str
import importlib
import inspect
import json
import logging
import numpy as np
from past.builtins import str as old_str
from past.builtins import unicode
import past.utils
import sys

PRIMITIVES = (int, float, str, bool, int, str, old_str, unicode, type(None))


def old_div(x, y):
    """Ensures that numpy performs integer division if array in
       denominator has integer type.
    """
    if type(y) is np.ndarray and len(y.shape) == 1 and issubclass(y.dtype.type, np.integer):
        return x // y
    else:
        return past.utils.old_div(x, y)


def class_to_dict(inst, ignore_list=[], attr_prefix=''):
    """ Writes state of class instance as a dict
        Includes both attributes and properties (i.e. those methods labeled with @property)
        Note: because this capture properties, it should be viewed as a snapshot of instance state
    :param inst:  instance to represent as dict
    :param ignore_list: list of attr
    :return: dict
    """
    output = vars(inst).copy()  # captures regular variables
    cls = type(inst)  # class of instance
    properties = [p for p in dir(cls) if isinstance(getattr(cls, p), property)]
    for p in properties:
        prop = getattr(cls, p)  # get property object by name
        output[p] = prop.fget(inst)  # call its fget
    for k in list(output.keys()):  # filter out dict keys mentioned in ignore-list
        if k in ignore_list:
            del output[k]
        else:  # prepend attr_prefix
            output[attr_prefix + k] = output.pop(k)

    output[attr_prefix + 'class'] = cls.__name__
    return output


def sanitize_for_db(field):
    if field == None:
        return 'NULL'
    elif type(field) == int:
        return repr(int(field))
    elif type(field) == str and "'" in field:
        from psycopg2.extensions import adapt
        return str(adapt(field))
    else:
        return repr(field)


def prepare_for_hash(item):
    if type(item) == str and sys.version_info >= (3, 0):
        return item.encode('utf-8')

    return item


def prepare_for_db(payload):
    return sanitize_for_db(json.dumps(prepare_for_json(payload)))


def init_params_from_locals(locals):
    params = {}

    for k, v in locals.items():
        if k == 'self' or k == '__class__':
            continue

        if 'marshal' in dir(v):
            params[k] = v.marshal()
        else:
            params[k] = v

    return params


def contains_superclass(obj, classname):
    if not inspect.isclass(obj):
        return False

    superclasses = [cls.__name__ for cls in inspect.getmro(obj)]

    return classname in superclasses


def prepare_for_json(item):
    """Operates on PRIMITIVES, dicts, numpy.array, and persistable 
       objects. 
    """
    if type(item) in PRIMITIVES:
        return item
    elif 'marshal' in dir(item):
        return item.marshal()
    elif contains_superclass(type(item), 'Inspectable'):
        return prepare_for_json(item.inspect())
    elif type(item) == np.ndarray:
        return {'ndarray': item.tolist(), 'shape': item.shape}
    elif type(item) == list or type(item) == tuple:
        replacement = []

        for x in item:
            replacement.append(prepare_for_json(x))

        return replacement
    elif type(item) == dict:
        replacement = {}

        for k, v in item.items():
            k = str(k)
            replacement[k] = prepare_for_json(v)

        return replacement
    else:
        # attempt to coerce numpy scalars
        try: return float(item)
        except: pass

        raise TypeError('not supported by prepare_for_json')


def receive_from_json(item):
    """Operates on json strings formed with prepare_from_json.
    """
    if type(item) in PRIMITIVES:
        return item
    elif type(item) == dict and 'ndarray' in item and 'shape' in item:
        return np.array(item['ndarray']).reshape(item['shape'])
    elif type(item) == dict and 'marshaled' in item:
        return get_class(item['class']).unmarshal(item['init_params'])
    elif type(item) == list or type(item) == tuple:
        replacement = []

        for x in item:
            replacement.append(receive_from_json(x))

        return replacement
    elif type(item) == dict:
        replacement = {}

        for k, v in item.items():
            replacement[k] = receive_from_json(v)

        return replacement
    else:
        raise TypeError('not supported by receive_from_json')


def get_class(qualified_class_name):
    class_parts = qualified_class_name.split('.')
    class_ = class_parts[-1]
    module_ = '.'.join(class_parts[:-1])

    module = importlib.import_module(module_)

    return getattr(module, class_)


def instantiate(qualified_class_name, init_params):
    return get_class(qualified_class_name)(**init_params)


def classname(obj):
    module_ = obj.__class__.__module__
    class_ = obj.__class__.__name__

    return module_ + '.' + class_


def standardize(item):
    """This method attempts to return common python objects
       to a standard form. It is typically used for post-
       processing output from json.loads.
    """
    if type(item) == tuple or type(item) == list:
        return list(map(standardize, item))
    elif type(item) == str:
        return str(item)
    elif type(item) == np.ndarray:
        return standardize(list(item))
    elif type(item) == dict:
        replacement = {}

        for k, v in item.items():
            replacement[str(k)] = standardize(v)

        return replacement
    else:
        # attempt to coerce numpy scalars
        try: return float(item)
        except: pass

    return item


def setup_logging(logger_name, log_file=None, log_level='DEBUG'):
    logger = logging.getLogger(logger_name)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    if log_file is None:
        handler = logging.StreamHandler(sys.stdout)
    else:
        handler = logging.FileHandler(log_file)

    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.getLevelName(log_level))

    return logger
