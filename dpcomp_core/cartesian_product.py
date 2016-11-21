import hashlib
import logging
from dpcomp_core.mechanism import dataset
from dpcomp_core.mechanism import metric
from dpcomp_core.mechanism import workload
from dpcomp_core.harness import experiment
from dpcomp_core import util

logger = logging.getLogger('dpcomp')


def D(nickname, scale, domain, seed):
    return dataset.DatasetSampledFromFile(nickname=nickname,
                                          sample_to_scale=scale,
                                          reduce_to_dom_shape=domain,
                                          seed=seed)


def W(dim, domain, size, seed):
    if dim == 1:
        return workload.Prefix1D(domain_shape_int=domain)
    elif dim == 2:
        return workload.RandomRange(shape_list=None,
                                    domain_shape=domain,
                                    size=size,
                                    seed=seed)


def E(d, w, a, epsilon, seed):
    return experiment.Single(d, w, a, epsilon, seed=seed)


def M(experiment):
    return metric.SampleError(experiment)


def config_hash(params):
    h = hashlib.sha1()
    h.update(params['nickname'])
    h.update(repr(params['dimension']))
    h.update(repr(params['epsilon']))
    h.update(repr(params['scale']))
    h.update(repr(params['domain']))
    h.update(repr(params['query_size']))
    h.update(params['algorithm'].hash)

    return h.hexdigest()

def cartesian_product(exp_seed, nickname_map, domain_map, algorithm_map, epsilons, scales, query_sizes, data_seed=0):
    params_list = []

    for nickname, dim in nickname_map.items():
        for epsilon in epsilons:
            for scale in scales[dim]:
                for domain in domain_map[dim]:
                    for algorithm in algorithm_map[dim]:
                        for query_size in query_sizes:
                            params_list.append({'nickname': nickname,
                                                'dimension': dim,
                                                'exp_seed': exp_seed,
                                                'data_seed': data_seed,
                                                'epsilon': epsilon,
                                                'scale': scale,
                                                'domain': domain,
                                                'query_size': query_size,
                                                'algorithm': algorithm})

    return params_list


def run(params):
    DOMAIN_SEED = 0
    WORK_SEED = 0

    d = D(params['nickname'], params['scale'], params['domain'], params['data_seed'])
    w = W(params['dimension'], params['domain'], params['query_size'], WORK_SEED)
    a = util.instantiate(util.classname(params['algorithm']), params['algorithm'].init_params)
    e = E(d, w, a, params['epsilon'], params['exp_seed'])
    m = M(e)
    m.compute()

    return m
