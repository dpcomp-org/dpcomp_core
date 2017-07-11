from builtins import range
import dpcomp_core.cartesian_product as cp
from dpcomp_core.execution import assemble_experiments
from dpcomp_core.execution import ListWriter
from dpcomp_core.execution import process_experiments
from dpcomp_core import util
from dpcomp_core import workload
from dpcomp_core.algorithm import BaseAlgorithm
import numpy as np
import pprint
'''
An example where a dummy custom algorithm is executed for a set of configurations.
To run your own algorithm, please modify the CustomAlg class, the algorithm will be called through its Run method.
Notes: 
- Please don't change the interface of the Run method.
- Please pass in any algorithm parameters through __init__. 
- Feel free to change foo or bar, but please keep short_name and give a readable name of your algorithm. 
- Please keep the line "self.init_params = util.init_params_from_locals(locals())" in __init__.
'''
class CustomAlg(BaseAlgorithm):

    def __init__(self, foo, bar, short_name='my alg'):
        self.init_params = util.init_params_from_locals(locals())
        self.short_name = short_name

    def Run(self, Q, x, epsilon, seed=None):
        return x + np.random.rand(*x.shape)

# experiment configuration specification, refer to simple_workflow for details
algorithms = {1: [CustomAlg(foo=42, bar='some string')], 2:[]}
datasets = {'HEPTH': 1, 'STROKE': 2}
scales = {1: [1e3],
          2: [1e7]}
domains = {1: [256],
           2: [(32,32)]}
workloads = {1: [workload.Prefix1D],
             2: [workload.RandomRange]}
query_sizes = [2000]
epsilons = [0.1]
ex_seeds = list(range(2))
ds_seeds = list(range(2))

# run experiments
writer = ListWriter()
params_map = assemble_experiments(algorithms, 
                                  datasets, 
                                  workloads,
                                  domains, 
                                  epsilons, 
                                  scales, 
                                  query_sizes, 
                                  ex_seeds, 
                                  ds_seeds)
process_experiments(params_map, writer)
writer.close()

# ouptput results
pp = pprint.PrettyPrinter()
pp.pprint([[repr(metric.analysis_payload()) for metric in group] for group in writer.metric_groups])
