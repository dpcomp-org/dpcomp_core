'''
Created on 30 mai 2011

@author: M
'''

class Bin:
    
    def __init__(self, count, id, interior = False):
	self.count = int(count)
	self.noisy_count = self.count
        self.id = id
        self.interior = interior

    
