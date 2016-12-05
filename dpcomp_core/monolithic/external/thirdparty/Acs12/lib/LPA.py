'''
@author: Gergely Acs <acs@crysys.hu>
'''

from Utils import *

def LPA(vec, sensitivity, eps):
    return map(lambda x: x + laplace(float(sensitivity)/eps), vec)

