'''
@author: Gergely Acs <acs@crysys.hu>
'''
from __future__ import division
from __future__ import absolute_import

from builtins import zip
from builtins import range
from builtins import object
from math import *
from .Bin import *
from . import Utils
import numpy as np
from . import ExpMechanism
from .ExpMechanism import *
import sys
from .cutils import *
from dpcomp_core import util


class Cluster(object):

    def __init__(self, bins, b_count, level = 1, do_update = True):
        self.bins = list(bins)
        self.level = level
        self.b = b_count
        self.ready = False
        self.error = None
        self.noisy_centroid = None

        if do_update and len(bins) > 0:
            self.update_error()

    def __len__(self):
        return len(self.bins)

    def update_error(self):
        self.noisy_centroid = np.mean(self.noisy_counts())
        self.error = fsum([abs(x.noisy_count -
                                           self.noisy_centroid) for x in self.bins]) + self.b

    def __repr__(self):
        return self.noisy_counts().__repr__()

    def perturb(self,prng):
        real_centroid = np.mean(self.real_counts())
        noisy_val = max(0, real_centroid + (util.old_div(prng.laplace(0,self.b), len(self))) )
        # noisy_val = real_centroid
        for i in range(len(self)):
            self.bins[i].noisy_count = noisy_val

    def noisy_counts(self):
        return [x.noisy_count for x in self.bins]

    def real_counts(self):
        return [x.count for x in self.bins]

    def update_output(self, output):
        for bin in self.bins:
            output[bin.id] = bin.noisy_count

    def split(self, pos):
        c1 = Cluster(self.bins[0:pos], self.b, self.level + 1)
        c2 = Cluster(self.bins[pos:len(self)], self.b, self.level + 1) 
        return [c1, c2]

        
class Clustering(object):
    
    def __init__(self, eps_cluster, eps_count, sensitivity, max_depth, max_cl_num = 200):
        self.eps_cluster = eps_cluster
        self.eps_count = eps_count
        self.sensitivity = sensitivity
        self.max_cl_num = max_cl_num
        self.max_depth = max_depth

    def split(self,clusters):
        err = fsum([x.error for x in clusters])
        priv_items = [PrivItem(-err,[0, 0])]

        # navigate to the first non-ready cluster
        for cluster in clusters:
            if not cluster.ready:
                break

        # calling C implementation from cutils
        split_errors = clustersplit(cluster.noisy_counts())

        for i in range(len(split_errors)):
            priv_items.append(PrivItem(-err+cluster.error-split_errors[i][0]-2*cluster.b, [cluster, i+1]))

        #item = max(priv_items,key=lambda x:x.q)
        item = ExpMechanism.run(priv_items,util.old_div((self.eps_cluster*0.5),self.max_depth), 2*self.sensitivity)

        old_cluster = cluster
        cluster = item.id[0]
        if cluster == 0:
            old_cluster.ready = True
            return False
        else:
            clusters.remove(cluster)
            children = cluster.split(item.id[1])
            for c in children:
                if len(c) == 1 or c.level == self.max_depth:
                    c.ready = True
            clusters.extend(children)
            return True

        
    # divisible clustering
    def topDown(self, cluster, priv_items):
        to_process = [cluster]
        n = len(cluster)

        while len(to_process) < n and len(to_process) <= self.max_cl_num:
            #print "\rBuffer: %d   " % (len(to_process)),
            c = self.split(to_process) 

            if c == False:
                if any((not c.ready for c in to_process)):
                    err = fsum([x.error for x in to_process])
                    priv_items.append(PrivItem(-err, list(to_process)))
                    continue
                else:
                    break

            err = fsum([x.error for x in to_process])
            priv_items.append(PrivItem(-err, list(to_process)))


    def run(self, vec,prng):
        bins = [Bin(*x) for x in zip(vec, list(range(len(vec))))]

        vec = [x.count for x in bins]

        # noisy_count is real count now
        for i in range(len(vec)):
            bins[i].noisy_count = max(vec[i], 0) 

        cluster = Cluster(bins, util.old_div(self.sensitivity, self.eps_count)) 

        priv_items = [PrivItem(-cluster.error, [cluster])]
        self.topDown(cluster, priv_items)
        #clusters = max(priv_items,key=lambda x:x.q).id
        clusters = ExpMechanism.run(priv_items, self.eps_cluster*0.5, 2 * self.sensitivity).id

        #print >> sys.stderr, "Number of clusters", len(clusters)

        # perturbing real counts based on the formed clusters
        for cluster in sorted(clusters, key = lambda x:x.noisy_centroid):
            cluster.update_error()
            cluster.perturb(prng)

        return [x.noisy_count for x in sorted(bins, key = lambda x:x.id)]

        

