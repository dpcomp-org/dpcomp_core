from builtins import range
import dpcomp_core.cartesian_product as cp
from dpcomp_core.execution import assemble_experiments
from dpcomp_core.execution import ListWriter
from dpcomp_core.execution import process_experiments
from dpcomp_core import workload
from dpcomp_core.algorithm import identity, HB, AG, uniform
from dpcomp_core import util
import pprint
'''
Example workflow where multiple algorithms/datasets/workloads etc could be specified.
Every valid combination of the configurations will be executed. The dictionary keys (1 or 2) stand for dimension. 
1D algorithms only work with 1D data/workload, and 2S algorithms only work with 2D data/workload.

Here in this example, 4 algorithms are specified. For each algorithm, there are two valid dataset instances and one valid workload.
Each valid configuration is executed twice with different experiment seeds.
In conclusion, the following code is specifying 4 runs for each of the 4 algorithms.
'''
# experiment configuration specification

## algorithm specification. 4 algorithms: 1D x 2, 2D x 2 
algorithms = {1: [identity.identity_engine(), HB.HB_engine()],
              2: [AG.AG_engine(), uniform.uniform_noisy_engine()]}

## dataset specification. 2 datasets: 1D x 1, 2D x 1
datasets = {'HEPTH': 1, 'STROKE': 2}
scales = {1: [1e3],
          2: [1e7]}
domains = {1: [256],
           2: [(32,32)]}
## dataset sampling seeds, used to generate different data instances based on the same dataset configuration.
ds_seeds = list(range(2)) 

## workload specification. 2 workloads: 1D x 1, 2D x 1
workloads = {1: [workload.Prefix1D],
             2: [workload.RandomRange]}
query_sizes = [2000]

## privacy level epsilon 
epsilons = [0.1]

## experiment seeds 
ex_seeds = list(range(2))


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


