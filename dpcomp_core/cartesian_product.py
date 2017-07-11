import hashlib
import logging
from dpcomp_core import dataset
from dpcomp_core import metric
from dpcomp_core import workload
from dpcomp_core import experiment
from dpcomp_core import util

logger = logging.getLogger('dpcomp')


def D(nickname, scale, domain, seed):
    return dataset.DatasetSampledFromFile(nickname=nickname,
                                          sample_to_scale=scale,
                                          reduce_to_dom_shape=domain,
                                          seed=seed)


def W(dim, domain, size, workclass, seed):
    if workclass == workload.Prefix1D:
        return workload.Prefix1D(domain_shape_int=domain)
    elif util.contains_superclass(workclass, 'RandomRange'):
        if dim == 1:
            domain = [domain]

        if util.contains_superclass(workclass, 'SimpleRandomRange'):
            return workclass(domain_shape=domain,
                              size=size,
                              seed=seed)
        else:
            return workload.RandomRange(shape_list=None,
                                        domain_shape=domain,
                                        size=size,
                                        seed=seed)
    else:
        raise TypeError('unsupported workload class %s' % repr(workclass))


def E(d, w, a, epsilon, seed):
    return experiment.Single(d, w, a, epsilon, seed=seed)


def M(experiment):
    return metric.SampleError(experiment)


def config_hash(params):
    h = hashlib.sha1()
    h.update(util.prepare_for_hash(params['nickname']))
    h.update(util.prepare_for_hash(repr(params['dimension'])))
    h.update(util.prepare_for_hash(repr(params['epsilon'])))
    h.update(util.prepare_for_hash(repr(params['scale'])))
    h.update(util.prepare_for_hash(repr(params['domain'])))
    h.update(util.prepare_for_hash(repr(params['query_size'])))
    h.update(util.prepare_for_hash(params['algorithm'].hash))

    return h.hexdigest()

def cartesian_product(exp_seed, 
                      nickname_map, 
                      domain_map, 
                      algorithm_map, 
                      epsilons, 
                      scales, 
                      query_sizes, 
                      workload_map={1: [workload.Prefix1D], 2: [workload.RandomRange]}, 
                      data_seed=0):
    params_list = []

    for nickname, dim in list(nickname_map.items()):
        for epsilon in epsilons:
            for scale in scales[dim]:
                for domain in domain_map[dim]:
                    for algorithm in algorithm_map[dim]:
                        for workload_class in workload_map[dim]:
                            for query_size in query_sizes:
                                params_list.append({'nickname': nickname,
                                                    'dimension': dim,
                                                    'exp_seed': exp_seed,
                                                    'data_seed': data_seed,
                                                    'epsilon': epsilon,
                                                    'scale': scale,
                                                    'domain': domain,
                                                    'query_size': query_size,
                                                    'algorithm': algorithm,
                                                    'workclass': workload_class})

    return params_list


def run(params):
    DOMAIN_SEED = 0
    WORK_SEED = 0

    d = D(params['nickname'], params['scale'], params['domain'], params['data_seed'])
    w = W(params['dimension'], params['domain'], params['query_size'], params['workclass'], WORK_SEED)
    a = util.instantiate(util.classname(params['algorithm']), params['algorithm'].init_params)
    e = E(d, w, a, params['epsilon'], params['exp_seed'])
    m = M(e)
    m.compute()

    return m
