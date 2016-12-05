'''
@author: Gergely Acs <acs@crysys.hu>
'''

from Utils import *
import random
from ExpMechanism import *
import ExpMechanism
import cmath

def SPA(data, l2_sens, eps):
    coeffs = dft(data)
     
    n = len(coeffs)
    lamb = math.sqrt(2) * l2_sens / eps
    priv_items = []
    s = sum(map(lambda x:abs(x)**2, coeffs))
    d = 0
    for i in xrange(1, n+1):
        d += abs(coeffs[i-1])**2
        Fni = s - d
        U = math.sqrt(Fni) + float(i) * math.sqrt(n) / eps
        priv_items.append(PrivItem(-U,i))

    item = ExpMechanism.basic(priv_items, 1.0 / lamb)
    k = item.id
    g = random.gammavariate((k+1)/2.0, 1.0 / lamb**2)
    for j in xrange(n):
        if j < k:
            (magn, phi) = cmath.polar(coeffs[j])
            coeffs[j] = cmath.rect(magn + random.normalvariate(0, math.sqrt(g)), phi)
        else:
            coeffs[j] = 0
    return map(lambda x: x.real, idft(coeffs))





