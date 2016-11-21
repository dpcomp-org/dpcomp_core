import dpcomp_core.cartesian_product as cp
from dpcomp_core.execution import assemble_experiments
from dpcomp_core.execution import ListWriter
from dpcomp_core.execution import process_experiments
from dpcomp_core import util
from dpcomp_core.monolithic import BaseAlgorithm
import numpy as np
import pprint


class CustomAlg(BaseAlgorithm):

    def __init__(self, foo, bar, short_name='my alg'):
        self.init_params = util.init_params_from_locals(locals())
        self.short_name = short_name

    def Run(self, Q, x, epsilon, seed=None):
        return x + np.random.rand(*x.shape)


algorithms = {1: [CustomAlg(foo=42, bar='some string')], 2:[]}
datasets = {'HEPTH': 1, 'STROKE': 2}
scales = {1: [1e3],
          2: [1e7]}
domains = {1: [256],
           2: [(32,32)]}
query_sizes = [2000]
epsilons = [0.1]
ex_seeds = range(2)
ds_seeds = range(2)

writer = ListWriter()
params_map = assemble_experiments(algorithms, datasets, domains, epsilons, scales, query_sizes, ex_seeds, ds_seeds)
process_experiments(params_map, writer)
writer.close()

pp = pprint.PrettyPrinter()
pp.pprint([[repr(metric.analysis_payload()) for metric in group] for group in writer.metric_groups])
