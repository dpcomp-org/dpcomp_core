from __future__ import division
from __future__ import absolute_import
from builtins import range
from builtins import object
import math
import numpy
from . import estimate_engine
from dpcomp_core import util

'''
Canonical name:     QuadTree (2D)
Additional aliases: -
Reference:          [G. Cormode, M. Procopiuc, E. Shen, D. Srivastava, and T. Yu. Differentially private spatial decompositions. ICDE, 2012.](http://dl.acm.org/citation.cfm?id=2310433)
Invocation:         dpcomp_core.algorithm.QuadTree.QuadTree_engine()
Implementation:     DPComp team
'''
class QuadTree_engine(estimate_engine.estimate_engine):
    '''self implementation of Quadtree with geometric budget splitting'''

    def __init__(self,short_name = "QuadTree"):
        self.init_params = util.init_params_from_locals(locals())
        self.short_name = short_name

    def Run(self, Q, x, epsilon,seed):
        assert seed is not None, 'seed must be set'
        prng = numpy.random.RandomState(seed)
        
        assert len(x.shape), '%s is defined for 2D data only' % self.__class__.__name__

        l1,l2 = x.shape
        
        
        height = math.ceil(math.log(int(math.sqrt(l1*l2)),2))
            

        l = int(2 ** height);
        newx = numpy.ndarray((l,l),'float32')
        newx.fill(0)
        for i in range(l1):
            newx[i][:l2] = x[i]

        
        acc = {}
        for i in range(l):
            acc[i] = {}
            acc[i][-1] = 0
            for j in range(l):
                acc[i][j] = acc[i][j-1] + newx[i][j]

        Root = HNode((0,0),(l-1,l-1),None,height)
        BuildTree(Root,acc,newx,(0,0),(l-1,l-1),2,epsilon,height,height,prng)

        WeightAvg(Root,epsilon,height)
        MeanConst(newx,Root,0,height)

        outputx = numpy.ndarray((l1,l2),'float32')
        for i in range(l1):
            outputx[i] = newx[i][:l2]
        return outputx




class HNode(object):
    def __init__(self,start,end,count,height):
        self.start = start
        self.end = end
        self.count = count
        self.height = height
        self.children = []
        self.parent = None

    def isleaf(self):
        return len(self.children) == 0



def BuildTree(Node,acc,X,start,end,b,epsilon,height,toth,prng):
    ''' Build the tree on X based on branching 2 and compute noisy count'''
    if height == 0:
        eps = 2**((toth - height)*1.0/3) * epsilon * (2**(util.old_div(1.0,3)) -1)/(2**((toth+1)*1.0/3)-1)
        nv = X[start[0]][start[1]] + prng.laplace(0.0,util.old_div(1.0,eps))
        Node.count = nv

    else:
        gridx = [int(util.old_div((end[0] - start[0] + 1),b))]*b
        left = end[0] - start[0] + 1 - sum(gridx)
        for i in range(left):
            gridx[i] = gridx[i] + 1

        gridy = [int(util.old_div((end[1] - start[1] + 1),b))]*b
        left = end[1] - start[1] + 1 - sum(gridy)
        for i in range(left):
            gridy[i] = gridy[i] + 1
            
        newgridx = []
        newgridy = []
        for x in gridx:
            if x != 0:
                newgridx = newgridx + [x]
        for y in gridy:
            if y != 0:
                newgridy = newgridy + [y]
                
        for i in range(len(newgridx)-1):
            newgridx[i+1] = newgridx[i+1] + newgridx[i]
        for i in range(len(newgridy)-1):
            newgridy[i+1] = newgridy[i+1] + newgridy[i]
                
        newgridy = [0] + newgridy
        newgridx = [0] + newgridx

        for i in range(len(newgridx)-1):
            for j in range(len(newgridy)-1):
                x0,y0 = start[0] + newgridx[i], start[1] + newgridy[j]
                x1,y1 = start[0] + newgridx[i+1] - 1, start[1] + newgridy[j+1] - 1
                
                newN = HNode((x0,y0),(x1,y1),None,height-1)
                newN.parent = Node
                Node.children = Node.children + [newN]
                            
                BuildTree(newN,acc,X,(x0,y0),(x1,y1),b,epsilon,height - 1,toth,prng)
            
        tot = 0;
        for i in range(start[0],end[0]+1):
	        tot = tot + acc[i][end[1]] - acc[i][start[1]-1]
        
        eps = 2**((toth - height)*1.0/3) * epsilon * (2**(util.old_div(1.0,3)) -1)/(2**((toth+1)*1.0/3)-1)

        ntot = tot + prng.laplace(0.0, util.old_div(1.0,eps))
        Node.count = ntot

def WeightAvg(Node,epsilon,toth):
    ''' First postprocessing: Weighted averaging (in section 3.3)'''
    if Node.isleaf() == True:
        return
        
    for ch in Node.children:
        WeightAvg(ch,epsilon,toth)
    
    if Node.count != None:
        eps1 = 2**((toth - Node.height)*1.0/3) * epsilon * (2**(util.old_div(1.0,3)) -1)/(2**((toth+1)*1.0/3)-1)
        eps2 = 2**((toth - Node.height + 1)*1.0/3) * epsilon * (2**(util.old_div(1.0,3)) -1)/(2**((toth+1)*1.0/3)-1)

        alpha = 4*eps1**2 / (4*eps1**2 + eps2**2);
 
        tot = 0
        for x in Node.children:
            tot = tot + x.count
                
        Node.count = alpha * Node.count + (1-alpha) * tot


def MeanConst(X,Node,cursum,height):
    ''' Second postprocessing: Mean consistency (in section 3.3)'''
    if Node.height == height:
        if Node.isleaf():
            X[Node.start[0]][Node.start[1]] = Node.count
        else:
            tot = 0
            for ch in Node.children:
                tot = tot + ch.count
                    
            for ch in Node.children:
                MeanConst(X,ch,tot,height)
    
    else:
        pn = Node.parent.count
        Node.count = Node.count + 1.0 / 4 * (pn - cursum)

        if Node.isleaf():
            X[Node.start[0]][Node.start[1]] = Node.count
        else:
            tot = 0
            for ch in Node.children:
                tot = tot + ch.count
                    
            for ch in Node.children:
                MeanConst(X,ch,tot,height)

