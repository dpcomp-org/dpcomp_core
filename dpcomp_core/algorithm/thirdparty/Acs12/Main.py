'''
@author: Gergely Acs <acs@crysys.hu>
'''
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

from builtins import str
from .lib.SPA import *
from .lib.LPA import *
from .lib.Histogram import *
from .lib.EFPA import *
from .lib.Clustering import *
from .lib.Utils import *
from dpcomp_core import util

import math
import os

def run(dataset, budget, sensitivity, max_cl, attr):  

    print("\n==== Dataset:", dataset)
    
    histogram_name = dataset + ".txt"
    output_dir = os.getcwd() + "/output/"
    input_dir = os.getcwd() + "/datasets/%s/" % (dataset)
    
    b = util.old_div(sensitivity, budget)
    print("Budget:", budget)
    eps_cluster = budget * 0.5
    eps_count = budget * 0.5

    print("Attributed:", attr) 

    # Reading input histogram
    input = Histogram()
    input.loadFromFile(input_dir + histogram_name)

    if attr == "unattr":
        print("Histogram is ordered.")
        input = input.sort()

    print("Number of bins: %d" % (len(input))) 
 
    # SPA
    output = Histogram(SPA(input.bins, math.sqrt(sensitivity), budget))

    output.dump(output_dir + dataset + "-SPA-" + str(budget) + "-" + attr + ".txt") 

    print("\nSPA error; MRE:", input.MAP(output), "RMS:", input.l2distance(output)) 
    print("Statistical distance: ", output.normalize().stat_dist(input.normalize())) 
    print("KL-div: ", input.normalize().kl_div(output.normalize(sanitize=True))) 

    # EFPA
    output = Histogram(EFPA(input.bins, math.sqrt(sensitivity), budget))

    output.dump(output_dir + dataset + "-EFPA-" + str(budget) + "-" + attr + ".txt") 

    print("\nEFPA error; MRE:", input.MAP(output), "RMS:", input.l2distance(output)) 
    print("Statistical distance: ", output.normalize().stat_dist(input.normalize())) 
    print("KL-div: ", input.normalize().kl_div(output.normalize(sanitize=True))) 

    # Laplace
    output = Histogram(LPA(input.bins, sensitivity, budget))

    output.dump(output_dir + dataset + "-LPA-" + str(budget) + "-" + attr + ".txt") 

    print("\nLPA error; MRE:", input.MAP(output), "RMS:", input.l2distance(output)) 
    print("Statistical distance: ", output.normalize().stat_dist(input.normalize())) 
    print("KL-div: ", input.normalize().kl_div(output.normalize(sanitize=True))) 


    # P-HPartition

    output = Histogram(Clustering(eps_cluster, eps_count, sensitivity,
                        int(math.log(len(input),2)), max_cl).run(input.bins))

    output.dump(output_dir + dataset + "-PHP-" + str(budget) + "-" + attr + ".txt") 

    print("\nP-HP error; MRE:", input.MAP(output), "RMS:", input.l2distance(output)) 
    print("Statistical distance: ", output.normalize().stat_dist(input.normalize())) 
    print("KL-div: ", input.normalize().kl_div(output.normalize(sanitize=True))) 


# Entry point

if __name__ == "__main__":

    budget = 0.01
    sensitivity = 1.0
    max_cluster_num = 400

    for attr in ["unattr", "attr"]:
        run("waitakere", budget, sensitivity, max_cluster_num, attr)




              


