'''
@author: Gergely Acs <acs@crysys.hu>
'''
from __future__ import division
from __future__ import absolute_import

from builtins import range
from .Utils import *
import random
from .ExpMechanism import *
from . import ExpMechanism
import cmath
from dpcomp_core import util

def SPA(data, l2_sens, eps):
    coeffs = dft(data)
     
    n = len(coeffs)
    lamb = math.sqrt(2) * l2_sens / eps
    priv_items = []
    s = sum([abs(x)**2 for x in coeffs])
    d = 0
    for i in range(1, n+1):
        d += abs(coeffs[i-1])**2
        Fni = s - d
        U = math.sqrt(Fni) + float(i) * math.sqrt(n) / eps
        priv_items.append(PrivItem(-U,i))

    item = ExpMechanism.basic(priv_items, util.old_div(1.0, lamb))
    k = item.id
    g = random.gammavariate(util.old_div((k+1),2.0), util.old_div(1.0, lamb**2))
    for j in range(n):
        if j < k:
            (magn, phi) = cmath.polar(coeffs[j])
            coeffs[j] = cmath.rect(magn + random.normalvariate(0, math.sqrt(g)), phi)
        else:
            coeffs[j] = 0
    return [x.real for x in idft(coeffs)]





