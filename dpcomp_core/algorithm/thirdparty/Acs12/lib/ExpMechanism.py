'''
Created on 16 juin 2011

'''
from __future__ import division

from builtins import object
import math
import random
from dpcomp_core import util

class PrivItem(object):

     def __init__(self, q, id):
        self.id = id
        self.q = q
        self.error = None

def basic(items, f, debug=False):
    for item in items:
        item.error = f * item.q

    maximum = max([x.error for x in items])

    for item in items:
        item.error = math.exp(item.error - maximum)

    uniform = sum([x.error for x in items]) * random.random()

    for item in items:
        uniform -= item.error
        if uniform <= 0:
            break

    return item


def run(items, eps, q_sens,debug=False):
    return basic(items, util.old_div(eps, (2.0 * q_sens)),debug)


	
        
        
