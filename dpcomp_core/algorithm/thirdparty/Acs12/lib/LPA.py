'''
@author: Gergely Acs <acs@crysys.hu>
'''
from __future__ import division
from __future__ import absolute_import

from .Utils import *
from dpcomp_core import util

def LPA(vec, sensitivity, eps):
    return [x + laplace(util.old_div(float(sensitivity),eps)) for x in vec]

