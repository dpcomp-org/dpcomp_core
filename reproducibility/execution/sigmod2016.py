"""SIGMOD Data Generator 0.1

Usage:
    sigmod2016.py list (algorithms | datasets | scales | domains)
    sigmod2016.py run [--out=<out>] [--a1=<a1>] [--a2=<a2>] [--x1=<x1>] [--x2=<x2>] [--d1=<d1>] [--d2=<d2>] [--s1=<s1>] [--s2=<s2>] [--se=<se>] [--sd=<sd>]
    sigmod2016.py (-h | --help)
    sigmod2016.py --version

Options:
    -h --help       Show this screen.
    --out=<out>     Output file [default: benchmark.json]
    --a1=<a1>       1D Algorithms [default: ALL]
    --a2=<a2>       2D Algorithms [default: ALL]
    --x1=<x1>       1D Datasets [default: ALL]
    --x2=<x2>       2D Datasets [default: ALL]
    --d1=<d1>       1D Domains [default: ALL]
    --d2=<d2>       2D Domains [default: ALL]
    --s1=<s1>       1D Scales [default: ALL]
    --s2=<s2>       2D Scales [default: ALL]
    --se=<se>       Number of Execution Seeds [default: 5]
    --sd=<sd>       Number of Dataset Seeds [default: 5]
    --version       Show version.
"""

import dpcomp_core.cartesian_product as cp
from dpcomp_core.execution import assemble_experiments
from collections import defaultdict
from docopt import docopt
from joblib import Parallel, delayed
import json
import logging
from dpcomp_core.monolithic import *
import numpy as np
import os
import re
import sys
from dpcomp_core import util

PROCS = 1

util.setup_logging('dpcomp', os.path.join(os.environ['DPCOMP_LOG_PATH'], 'sigmod2016.out'), os.environ['DPCOMP_LOG_LEVEL'])

ALGORITHMS_MAP = {1: {alg.short_name: alg for alg in [identity.identity_engine(), HB.HB_engine(), mwemND.mwemND_adaptive_engine(index = "DEFALUT1D"), 
                                                      dawa.dawa_engine(ratio=0.25), thirdParty.php_engine(), mwemND.mwemND_engine(), thirdParty.efpa_engine(), 
                                                      DPcube1D.DPcube1D_engine(gz=11), ahpND.ahpND_adaptive_engine(index="DEFALUT1D"), 
                                                      thirdParty.StructureFirst_engine(), uniform.uniform_noisy_engine()]},
                  2: {alg.short_name: alg for alg in [identity.identity_engine(),  HB2D.HB2D_engine(), AG.AG_engine(),mwemND.mwemND_engine(),
                                                      mwemND.mwemND_adaptive_engine(index = "DEFALUT2D"),dawa2D.dawa2D_engine(ratio=0.25),
                                                      MyQuadTree.MyQuadTree_engine(), UG.UG_engine(), DPcube.DPcube_engine(gz=11), ahpND.ahpND_engine(), 
                                                      uniform.uniform_noisy_engine()]}}

DATASETS_MAP = {1: ['HEPTH', 'ADULTFRANK', 'INCOME', 'MEDCOST', 'NETTRACE',  
                    'PATENT', 'SEARCHLOGS', 'BIDS-FJ', 'BIDS-FM', 'BIDS-ALL',
                    'MDSALARY', 'MDSALARY-FA', 'LC-REQ-F1', 'LC-REQ-F2', 'LC-REQ-ALL',
                    'LC-DTIR-F1', 'LC-DTIR-F2', 'LC-DTIR-ALL', 'TWITTER'],
                2: ['SF-CABS-E', 'SF-CABS-S', 'GOWALLA', 'BEIJING-CABS-E',
                   'BEIJING-CABS-S', 'ADULT-2D', 'MDSALARY-OVERT',               
                   'LOAN-FUNDED-INCOME', 'STROKE', 'TWITTER']}

SCALES_MAP = {1: [1E3, 1E4, 1E5, 1E6, 1E7, 1E8],
              2: [1E3, 1E4, 1E5, 1E6, 1E7, 1E8]}

DOMAINS_MAP = {1: [256, 512, 1024, 2048, 4096],
               2: [(32,32), (64,64), (128,128), (256,256)]}

QUERY_SIZE = 2000
ALL_EXP_SEEDS = range(4)
EPSILON = 0.1


def extract_group_view(metrics):
    if len(metrics) == 0:
        return

    d_dimensionality = len(metrics[0].E.X.domain_shape)
    d_domain_size = metrics[0].E.X.domain_shape[0] #if d_dimensionality == 2 else metrics[0].E.X.domain_shape[0]

    return {'mean_error': np.mean(map(lambda metric: metric.error_payload['TypeI.L2'], metrics)),
            'stddev_error': np.std(map(lambda metric: metric.error_payload['TypeI.L2'], metrics), ddof=1),
            'e_hash': metrics[0].E.hash,
            'x_hash': metrics[0].E.X.hash,
            'epsilon': metrics[0].E.epsilon,
            'a_name': metrics[0].E.A.short_name,
            'w_name': metrics[0].E.W.pretty_name,
            'd_dimensionality': d_dimensionality,
            'd_domain_size':  d_domain_size,
            'd_scale': metrics[0].E.X.scale,
            'd_nickname': metrics[0].E.X.fname}


def process_experiments(params_map, fd):
    begin = True
    fd.write('[')

    for config_hash, params_list in params_map.iteritems():
        if PROCS > 1:
            group_metrics = Parallel(n_jobs=PROCS)(delayed(cp.run)(params) for params in params_list)
        else:
            group_metrics = [cp.run(params) for params in params_list]

        group_view = extract_group_view(group_metrics)

        if not begin:
            fd.write(', ')
        else:
            begin = False

        fd.write(json.dumps(group_view))

    fd.write(']')


def dispatch(arguments):
    if arguments['list'] and arguments['algorithms']:
        print '\n1D Algorithms:', ALGORITHMS_MAP[1].keys(), '\n'
        print '2D Algorithms:', ALGORITHMS_MAP[2].keys(), '\n'
    elif arguments['list'] and arguments['datasets']:
        print '\n1D Datasets:', DATASETS_MAP[1], '\n'
        print '2D Datasets:', DATASETS_MAP[2], '\n'
    elif arguments['list'] and arguments['scales']:
        print '\nScales:', ALL_SCALES, '\n'
    elif arguments['list'] and arguments['domains']:
        print '\n1D Domains:', DOMAINS_MAP[1], '\n'
        print '2D Domains:', DOMAINS_MAP[2], '\n'
    elif arguments['run']:
        outfile = arguments['--out']

        if arguments['--a1'] == 'ALL':
            a1 = ALGORITHMS_MAP[1].values()
            a1p = ALGORITHMS_MAP[1].keys()
        else:
            a1 = map(lambda alg: ALGORITHMS_MAP[1][alg], arguments['--a1'].split(','))
            a1p = arguments['--a1'].split(',')

        if arguments['--a2'] == 'ALL':
            a2 = ALGORITHMS_MAP[2].values()
            a2p = ALGORITHMS_MAP[2].keys()
        else:
            a2 = map(lambda alg: ALGORITHMS_MAP[2][alg], arguments['--a2'].split(','))
            a2p = arguments['--a2'].split(',')

        if arguments['--x1'] == 'ALL':
            x1 = DATASETS_MAP[1]
        else:
            x1 = arguments['--x1'].split(',')

        if arguments['--x2'] == 'ALL':
            x2 = DATASETS_MAP[2]
        else:
            x2 = arguments['--x2'].split(',')

        if arguments['--d1'] == 'ALL':
            d1 = DOMAINS_MAP[1]
        else:
            d1 = map(int, arguments['--d1'].split(','))
            print d1

        if arguments['--d2'] == 'ALL':
            d2 = DOMAINS_MAP[2]
        else:
            d2 = map(eval, re.findall('(\([\d]+,[\s]*[\d]+\))', arguments['--d2']))

        if arguments['--s1'] == 'ALL':
            s1 = SCALES_MAP[1]
        else:
            s1 = map(eval, arguments['--s1'].split(','))

        if arguments['--s2'] == 'ALL':
            s2 = SCALES_MAP[2]
        else:
            s2 = map(eval, arguments['--s2'].split(','))

        algorithms = {1: a1, 2: a2}
        datasets = {data: 1 for data in x1}
        datasets.update({data: 2 for data in x2})
        domains = {1: d1, 2: d2}
        scales = {1: s1, 2: s2}
        ex_seeds = range(int(arguments['--se']))
        ds_seeds = range(int(arguments['--sd']))

        if len(ds_seeds) * len(ex_seeds) < 2:
            print '\nerror: at least two seed are required\n'
            sys.exit(1)

        print '\nRunning with the following arguments', '\n'
        print '\tOutfile:', outfile, '\n'
        print '\tAlgorithms:', {1: a1p, 2: a2p}, '\n'
        print '\tDatasets:', {1: x1, 2: x2}, '\n'
        print '\tDomains:', domains, '\n'
        print '\tScales:', scales, '\n'
        print '\tExecution Seeds:', len(ex_seeds), '\n'
        print '\tDataset Seeds:', len(ds_seeds), '\n'

        params_map = assemble_experiments(algorithms, 
                                          datasets, 
                                          domains, 
                                          [EPSILON], 
                                          scales, 
                                          [QUERY_SIZE], 
                                          ex_seeds, 
                                          ds_seeds)

        with open(outfile, 'wb') as fd:
            process_experiments(params_map, fd)

if __name__ == "__main__":
    dispatch(docopt(__doc__, version='SIGMOD Data Generator 0.1'))
