'''
@author: Gergely Acs <acs@crysys.hu>
'''

from math import *
from Utils import *
import ExpMechanism
from ExpMechanism import *
import numpy as np
import cmath

def EFPA(data, l2_sens, eps,prng):
    data = map(float, data)
    coeffs = rfft(data)

    n = len(coeffs)

    eps_1 = eps_2 = eps * 0.5
    s = abs(coeffs[0])**2 
    for i in range(1,n-1):
        s += 2*abs(coeffs[i])**2 

    if len(data) % 2 == 0:
        s += abs(coeffs[n-1])**2 
    else:
        s += 2*abs(coeffs[n-1])**2 
    
    # DC coeff
    kept = 1
    d = abs(coeffs[0])**2
    sum = sqrt(s - d) + sqrt(2) *  kept * (l2_sens / eps_2)
    priv_items = [PrivItem(-sum, [0, kept])]
    
    # Other coeffs except the last one
    for i in xrange(1, n-1):
        kept += 2
        d += 2 * abs(coeffs[i])**2
        sum = sqrt(s - d) + sqrt(2) *  kept * (l2_sens / eps_2)
        #sum = sqrt(sum) * sqrt(kept)
        priv_items.append(PrivItem(-sum, [i, kept]))

    # last coeff needs special consideration depending len(data) is even or odd
    if len(data) % 2 == 0:
        kept += 1
        d += abs(coeffs[n-1])**2
    else:
        kept += 2
        d += 2 * abs(coeffs[n-1])**2

    sum = sqrt(s - d) + sqrt(2) *  kept * (l2_sens / eps_2)
    priv_items.append(PrivItem(-sum, [n, kept]))

    # maximal kept coeffs is upper bounded by the length data vector
    item = ExpMechanism.run(priv_items, eps_1, l2_sens)

    lamb = sqrt(item.id[1]) * l2_sens / eps_2
    k = item.id[0] + 1
    for j in range(n):
        if j < k:
            (magn, phi) = cmath.polar(coeffs[j])
            coeffs[j] = cmath.rect(magn + prng.laplace(0,lamb), phi)
        else:
            coeffs[j] = 0

    return map(lambda x: x.real,  irfft(coeffs, len(data)))


