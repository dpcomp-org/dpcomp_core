from __future__ import division
from __future__ import absolute_import
from builtins import range
from past.utils import old_div
from builtins import object
from . import estimate_engine
import math
import numpy
from dpcomp_core import util

'''
Canonical name:     HB (2D)
Additional aliases: -
Reference:          [W. Qardaji, W. Yang,and N. Li. Understanding hierarchical methods for differentially private histograms. PVLDB, 2013.](http://dl.acm.org/citation.cfm?id=2556576)
Invocation:         dpcomp_core.algorithm.HB2D.HB2D_engine()
Implementation:     DPComp team
'''
class HB2D_engine(estimate_engine.estimate_engine):
    '''Use hierarchical strategy from Hay PVLDB 2010 using branching from Qardaji PVLDB 2013.'''
    
    def __init__(self,br = 0, short_name ="HB"):
        #b control the branching, if b == 0, compute it based on expression in the paper

        self.init_params = util.init_params_from_locals(locals())
        self.br = br
        self.short_name = short_name
    

    def Run(self, Q, x, epsilon, seed):
        assert seed is not None, 'seed must be set'

        prng = numpy.random.RandomState(seed)

        assert len(x.shape)==2, '%s is defined for 2D data only' % self.__class__.__name__


        l1,l2 = x.shape
        
        if self.br == 0:
            b = find_best_branching(l1*l2)
        else:
            b = self.br
        
        height = math.ceil(math.log(int(math.sqrt(l1*l2)),b))
        
        l = int(b ** height);
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
        BuildTree(Root,acc,newx,(0,0),(l-1,l-1),b,epsilon*1.0/height,height,height,prng)

        WeightAvg(Root,b)
        for ch in Root.children:
            MeanConst(newx,ch,b,0,height)

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


def find_best_branching(N):
    '''Try all branchings from 2 to sqrt(N) and pick onewith minimum variance.'''
    min_v = float('inf')
    min_b = None
    n = int(math.sqrt(N))

    for b in range(2,n+1):
        v = variance(N, b)
        if v < min_v:
            min_v = v
            min_b = b
    return min_b

def variance(N, b):
    '''Computes variance given domain of size N and branchng factor b.  Equation in section 5.1.'''
    n = int(math.sqrt(N))
    h = math.ceil(math.log(n,b))

    return b * (n-1) * h**2

def BuildTree(Node,acc,X,start,end,b,epsilon,height,toth,prng):
    ''' Build the tree on X based on branching b and compute noisy count'''
    if height == 0:
        nv = X[start[0]][start[1]] + prng.laplace(0.0,old_div(1.0,epsilon))
        Node.count = nv

    else:
        gridx = [int(old_div((end[0] - start[0] + 1),b))]*b
        left = end[0] - start[0] + 1 - sum(gridx)
        for i in range(left):
            gridx[i] = gridx[i] + 1

        gridy = [int(old_div((end[1] - start[1] + 1),b))]*b
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
            
        if height < toth:
            tot = 0;
            for i in range(start[0],end[0]+1):
                tot = tot + acc[i][end[1]] - acc[i][start[1]-1]
                        
            ntot = tot + prng.laplace(0.0, old_div(1.0,epsilon))
            Node.count = ntot

def WeightAvg(Node,b):
    ''' First postprocessing: Weighted averaging (in section 3.3)'''
    if Node.isleaf() == True:
        return
        
    for ch in Node.children:
        WeightAvg(ch,b)
    
    if Node.count != None:
        br = b**2
        alpha = (br**(Node.height+1) - br**(Node.height)) *1.0/ (br**(Node.height+1) - 1)
        tot = 0
        for x in Node.children:
            tot = tot + x.count
                
        Node.count = alpha * Node.count + (1-alpha) * tot


def MeanConst(X,Node,b,cursum,height):
    ''' Second postprocessing: Mean consistency (in section 3.3)'''
    if Node.height == height - 1:
        if Node.isleaf():
            X[Node.start[0]][Node.start[1]] = Node.count
        else:
            tot = 0
            for ch in Node.children:
                tot = tot + ch.count
                    
            for ch in Node.children:
                MeanConst(X,ch,b,tot,height)
    
    else:
        pn = Node.parent.count
        Node.count = Node.count + 1.0 / (b**2) * (pn - cursum)

        if Node.isleaf():
            X[Node.start[0]][Node.start[1]] = Node.count
        else:
            tot = 0
            for ch in Node.children:
                tot = tot + ch.count
                    
            for ch in Node.children:
                MeanConst(X,ch,b,tot,height)




