import dpcomp_core.cartesian_product as cp
from dpcomp_core.execution import assemble_experiments
from dpcomp_core.execution import ListWriter
from dpcomp_core.execution import process_experiments
from dpcomp_core.mechanism import workload
from dpcomp_core.monolithic import *
from dpcomp_core import util
import pprint


algorithms = {1: [identity.identity_engine(), HB.HB_engine()],
              2: [AG.AG_engine(), uniform.uniform_noisy_engine()]}
datasets = {'HEPTH': 1, 'STROKE': 2}
scales = {1: [1e3],
          2: [1e7]}
domains = {1: [256],
           2: [(32,32)]}
workloads = {1: [workload.Prefix1D],
             2: [workload.RandomRange]}
query_sizes = [2000]
epsilons = [0.1]
ex_seeds = range(2)
ds_seeds = range(2)

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

pp = pprint.PrettyPrinter()
pp.pprint([[repr(metric.analysis_payload()) for metric in group] for group in writer.metric_groups])
