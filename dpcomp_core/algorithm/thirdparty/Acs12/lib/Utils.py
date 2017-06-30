'''
Created on 16 juin 2011

'''
from __future__ import division

from builtins import map
from builtins import range
import math
import random as rnd
import numpy as np
import scipy.fftpack
import cmath
from functools import reduce
from dpcomp_core import util

def KL_div(p, q):
    s = 0
    for i in range(len(p)):
        if p[i] > 0:
            s += p[i] * math.log(util.old_div(float(p[i]), q[i]))
    return s

def l2norm(values):
    return math.sqrt(reduce(lambda x,y: x + abs(y)**2, values))

def sanitize(hist):
    return [max(1, x) for x in hist]

def is_int(s):
    try:
        int(s)
        return True
    except ValueError:
        return False

def is_float(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def laplace(p_lambda):
    return np.random.laplace(0, p_lambda, 1)[0]

def normalize(vec):
    s = sum(vec)
    return  vec if s <= 0 else list(map((lambda x: util.old_div(x,float(s))), vec))

def stat_dist(d1, d2):
    return sum( (abs(d1[i] - d2[i]) for i in range(len(d1))) )

# numpy's fft is buggy, so we use scipy's fft
def rfft(vec):
    tmp = scipy.fftpack.rfft(vec) 
    coeffs = [tmp[0]+0*1j]
    i = 1
    while i <= len(tmp) - 2:
        coeffs.append(tmp[i]+tmp[i+1]*1j)
        i += 2
    if i != len(tmp):
        coeffs.append(tmp[i]+0*1j)

    return coeffs

def irfft(coeffs, size):
    tmp = [coeffs[0].real]
    for c in coeffs[1:]:
        tmp.extend([c.real, c.imag])

    if size % 2 == 0:
        del tmp[-1]

    return scipy.fftpack.irfft(tmp) 

def dft(vec):
    ## FOR ORIGINAL SPA
    return np.roll(np.fft.fft(vec),-1)
    #return np.fft.fft(vec)

def idft(coeffs):
    ## FOR ORIGINAL SPA
    return np.fft.ifft(np.roll(coeffs,1))
    #return np.fft.ifft(coeffs)

def crop(coeffs,k):
    coeffs[k:] = np.zeros(len(coeffs) - k)
    return coeffs

