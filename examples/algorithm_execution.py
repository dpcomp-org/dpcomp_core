from __future__ import division
from __future__ import print_function
from past.utils import old_div
from dpcomp_core.algorithm import AG
from dpcomp_core import dataset
from dpcomp_core import util
from dpcomp_core import workload
import numpy as np
'''
An example execution of one single algorithm. 
'''

domain = (32,32)
epsilon = 0.1
nickname = 'SF-CABS-E'
sample = 1E4
seed = 1
shape_list = [(5,5),(10,10)]
size = 1000

# Instantiate algorithm
a = AG.AG_engine(c=10, c2=5, alpha=.4)

# Instantiate dataset
d = dataset.DatasetSampledFromFile(nickname=nickname, 
                                     sample_to_scale=sample, 
                                     reduce_to_dom_shape=domain, 
                                     seed=111)

# Instantiate workload
w = workload.RandomRange(shape_list=shape_list, 
                         domain_shape=domain, 
                         size=size, 
                         seed=seed)

# Calculate noisy estimate for x
x = d.payload
x_hat = a.Run(w, x, epsilon, seed)

# Compute error between true x and noisy estimate
diff = w.evaluate(x) - w.evaluate(x_hat)
print('Per Query Average Absolute Error:', old_div(np.linalg.norm(diff,1), float(diff.size)))
