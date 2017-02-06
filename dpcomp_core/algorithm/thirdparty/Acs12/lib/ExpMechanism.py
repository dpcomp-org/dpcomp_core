'''
Created on 16 juin 2011

'''

import math
import random

class PrivItem:

     def __init__(self, q, id):
        self.id = id
        self.q = q
        self.error = None

def basic(items, f, debug=False):
    for item in items:
        item.error = f * item.q

    maximum = max(map(lambda x:x.error, items))

    for item in items:
        item.error = math.exp(item.error - maximum)

    uniform = sum(map(lambda x:x.error, items)) * random.random()

    for item in items:
        uniform -= item.error
        if uniform <= 0:
            break

    return item


def run(items, eps, q_sens,debug=False):
    return basic(items, eps / (2.0 * q_sens),debug)


	
        
        
