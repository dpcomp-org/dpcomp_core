from builtins import object
from collections import defaultdict
from dpcomp_core import cartesian_product as cp
from dpcomp_core import util
import json


class FileWriter(object):
    
    def __init__(self, fd):
        self._fd = fd
        self._closed = False
        self._begin = True

        self._fd.write('[')

    def write(self, metric_group):
        assert not self._closed

        if not self._begin:
            self._fd.write(', ')
        else:
            self._begin = False

        prepared_groups = [util.prepare_for_json(group.asDict()) for group in metric_group]
        self._fd.write(json.dumps(prepared_groups))

    def close(self):
        self._fd.write(']')

        self._closed = True


class ListWriter(object):
    
    def __init__(self):
        self.metric_groups = []
        self._closed = False

    def write(self, metric_group):
        assert not self._closed

        self.metric_groups.append(metric_group)

    def close(self):
        self._closed = True


def process_experiments(params_map, writer, procs=1):
    for config_hash, params_list in params_map.items():
        group_metrics = [cp.run(params) for params in params_list]

        writer.write(group_metrics)


def assemble_experiments(algorithms, datasets, workloads, domains, epsilons, scales, query_sizes, ex_seeds, ds_seeds):
    params_list = []
    for ex_seed in ex_seeds:
        for ds_seed in ds_seeds:
            params_list += cp.cartesian_product(ex_seed, 
                                                datasets, 
                                                domains, 
                                                algorithms, 
                                                epsilons, 
                                                scales, 
                                                query_sizes, 
                                                workloads,
                                                ds_seed)

    params_map = defaultdict(list)
    for params in params_list:
        params_map[cp.config_hash(params)].append(params)

    return params_map
