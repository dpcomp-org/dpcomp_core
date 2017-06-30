'''
@author: Gergely Acs <acs@crysys.hu>
'''
from __future__ import division
from __future__ import absolute_import

from builtins import map
from builtins import zip
from builtins import range
from builtins import object
from . import Utils
import numpy as np
import math
import random as rnd
import heapq
from dpcomp_core import util

class Histogram(object):

    def __init__(self, bins = [], normalized=False, bin_num=None):
        if bin_num != None:
            self.bins = np.zeros(bin_num)
        if len(bins) > 0:
            self.bins = np.array([max(x, 0) for x in bins])

        self.normalized = normalized

    def loadFromFile(self, filename, normalized = False,  lines = []):
        file = open(filename)
        bins = []
        i = 0
        for line in file:
            if not lines or i in lines:
                str = line.strip()
                if line.startswith('#') or line.startswith('//') or line.startswith('%'):
                    continue
                for val in line.split():
                    if Utils.is_int(val):
                        bins.append(int(val)) 
                    elif Utils.is_float(val):
                        bins.append(float(val))
            i += 1

        self.bins = np.array(bins)
        self.normalized = normalized

        file.close()

    def dump(self, filename):
        file = open(filename, 'w')

        file.write("\n".join(map(str, self.bins)))

        file.close()

    def sort(self): 
        return Histogram(sorted(self.bins)) 

    def resize(self, len):
        self.bins.resize(len)

    def max(self):
        return max(self.bins)

    def sample(self):
        assert self.normalized
        nonce = rnd.random()
        s = 0.0
        for i in range(len(self.bins)):
            s += self.bins[i]
            if s > nonce:
                break

        return i

    def isempty(self):
        return self.sum() == 0

    def mean(self):
        return np.mean(self.bins)

    def clone(self):
        return Histogram(np.array(self.bins), normalized=self.normalized) 

    def update(self, bins):
        self.bins = np.array([max(x, 0) for x in bins])

    def __getitem__(self,key):
        return self.bins[key]

    def __setitem__(self,key,val):
        self.bins[key] = val

    def count(self):
        return sum(self.bins)

    def sum(self):
        return self.count()

    def nullifyNaN(self):
        assert not self.normalized
        self.bins = [0 if math.isnan(x) else x for x in self.bins]

    def quantile(self, p):
        count = self.count()
        s = 0

        for i in range(len(self)):
            s += self.bins[i]
            if count > 0 and util.old_div(float(s), count) > p:
                return i - 1

        return 0
        

    def __add__(self,other):
        if isinstance(other,  (int, float)):
            return Histogram([x + other for x in self.bins]) 
        else:
            return Histogram(list(map(sum, list(zip(self.bins, other_bins)))))

    def __mul__(self,other):
        if isinstance(other,  (int, float)):
            return Histogram([x * other for x in self.bins]) 
        else:
            raise NameError('NotImplemented')

    def __imul__(self, other):
        if isinstance(other, (int, float)):
            self.bins = [x * other for x in self.bins]
            self.normalized = False
        else:
            raise NameError('NotImplemented')

        return self

    def __iadd__(self, other):
        if isinstance(other, (int, float)):
            self.bins = [x + other for x in self.bins]

        self.bins = list(map(sum, list(zip(self.bins, other.bins))))
        return self

    def __div__(self,other):
        if isinstance(other,  (int, float)):
            return Histogram([util.old_div(float(x), other) for x in self.bins]) 
        else:
            raise NameError('NotImplemented')

    def getTop(self, T):
        return [tuple(reversed(x)) for x in heapq.nlargest(T, [tuple(reversed(x)) for x in list(enumerate(self.bins))])]

    def getFirst(self, T):
        return list(enumerate(self.bins))[:T]

    def normalize(self, sanitize = False):
        #if self.normalized:
        #    return self

        h = self.bins
        if sanitize:
            h = Utils.sanitize(h)

        h = Utils.normalize(h)

        return Histogram(h, True) 

    def stat_dist(self, histogram):
        assert self.normalized and histogram.normalized
        return Utils.stat_dist(self.bins, histogram.bins)

    def sanity_bound(self):
        return 0.001 * self.sum()

    def MAP(self, histogram):
        sanity_bound = self.sanity_bound()
        return np.mean([util.old_div(math.fabs(x[0] - x[1]),
                   max(x[0],sanity_bound)) for x in zip(self.bins, histogram.bins)])

    def l1distance(self, histogram):
        return np.sum([math.fabs(x[0] - x[1]) for x in zip(self.bins, histogram.bins)])

    def l2distance(self, histogram):
        return math.sqrt(np.sum([(x[0] - x[1])**2 for x in zip(self.bins, histogram.bins)]))

    def MSE(self, histogram):
        return np.mean([(x[0] - x[1])**2 for x in zip(self.bins, histogram.bins)])

    def kl_div(self, histogram):
        assert self.normalized and histogram.normalized
        return Utils.KL_div(self.bins, histogram.bins) 

    def __repr__(self):
        return self.bins.__repr__()

    def __len__(self):
        return self.bins.__len__()

