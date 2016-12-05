import numpy as np
import logging
from Kd_standard import Kd_standard
from Params import Params
from collections import deque
from KNode import KNode
from Differential import Differential

class Hilbert(Kd_standard):
    """ Hilbert R-tree """
    def __init__(self, data, param):
        self.param = param
        self.differ = Differential(self.param.Seed)
        self.root = KNode()
        self.realData = data
        self.root.n_budget = Params.maxHeight
        
    def h_encode(self, x, y, r):
        """ (x,y) -> value h in Hilbert space, r is the resolution of the Hilbert curve """
        mask = (1 << r) - 1
        heven = x ^ y
        notx = ~x & mask
        noty = ~y & mask
        temp = notx ^ y
        v0, v1 = 0, 0
        for k in range(r-1):
            v1 = ((v1 & heven) | ((v0 ^ noty) & temp)) >> 1
            v0 = ((v0 & (v1 ^ notx)) | (~v0 & (v1 ^ noty))) >> 1
        hodd = (~v0 & (v1 ^ x)) | (v0 & (v1 ^ noty));
        return self.interleaveBits(hodd, heven)
    
    def h_decode(self, h, r):
        """ h -> (x,y) """
        heven, hodd = self.deleaveBits(h)
        mask = (1 << r) - 1
        v0, v1 = 0, 0
        temp1 = ~(heven | hodd) & mask
        temp0 = ~(heven ^ hodd) & mask
        for k in range(r-1):
            v1 = (v1^temp1) >> 1
            v0 = (v0^temp0) >> 1
        return (v0 & ~heven) ^ v1 ^ hodd, (v0 | heven) ^ v1 ^ hodd
    
    def interleaveBits(self, hodd, heven):
        val = 0;
        maxx = max(hodd, heven)
        n = 0
        while (maxx > 0):
            n += 1
            maxx >>= 1
        for i in range(n):
            bitMask = 1 << i
            a = 1 << (2*i) if (heven & bitMask) else 0
            b = 1 << (2*i+1) if (hodd & bitMask) else 0
            val += a + b
        return val
    
    def deleaveBitsOdd(self,x):
        x = x & 0x5555555555555555;
        x = (x | (x >> 1)) &  0x3333333333333333
        x = (x | (x >> 2)) &  0x0F0F0F0F0F0F0F0F
        x = (x | (x >> 4)) &  0x00FF00FF00FF00FF
        x = (x | (x >> 8)) &  0x0000FFFF0000FFFF
        x = (x | (x >> 16)) & 0x00000000FFFFFFFF
        return x
    
    def deleaveBits(self,x):
        return self.deleaveBitsOdd(x), self.deleaveBitsOdd(x >> 1)
    
    def get_Hcoord(self, x, y, R):
        hx = int((x - Params.LOW[0]) / (Params.HIGH[0] - Params.LOW[0] + 10 ** (-8)) * (2 ** R))
        hy = int((y - Params.LOW[1]) / (Params.HIGH[1] - Params.LOW[1] + 10 ** (-8)) * (2 ** R))
        return hx, hy

    def get_Rcoord(self, hx, hy, R):
        x = float(hx) / (2 ** R) * (Params.HIGH[0] - Params.LOW[0]) + Params.LOW[0]
        y = float(hy) / (2 ** R) * (Params.HIGH[1] - Params.LOW[1]) + Params.LOW[1]
        return x, y
    
    def getCount(self, curr, epsilon):
        count = len(curr.n_data)
        if epsilon < 10**(-6):
            return count
        else:
            return count + self.differ.getNoise(1,epsilon)
        
    def testLeaf(self, curr):
        """ test whether a node should be a leaf node """
        if (curr.n_depth == Params.maxHeight) or \
            (curr.n_budget <= 0) or \
            (curr.n_count <= self.param.minPartSize):
            return True
        return False
    
    def buildIndex(self):
        budget_c = self.getCountBudget()
        logging.debug('encoding coordinates...')
        RES = self.param.Res # order of Hilbert curve
        ndata = self.realData.shape[1]
        hidx = np.zeros(ndata)
        for i in range(ndata):
            hx,hy = self.get_Hcoord(self.realData[0,i],self.realData[1,i],RES)
            hidx[i] = self.h_encode(hx, hy, RES)
        hidx = np.sort(hidx)
        
        logging.debug('building index...')
        self.root.n_data = hidx
        self.root.n_box = (0, 2 ** (2 * RES) - 1)
        self.root.n_count = self.getCount(self.root,budget_c[0])
        
        stack = deque()
        stack.append(self.root)
        tree = []
        tree.append(self.root)
        leaf_li = [] # storage of all leaves
        nleaf = 0 # leaf counter
        max_depth = -1
        
        while len(stack) > 0:
            curr = stack.popleft()
            if curr.n_depth > max_depth:
                max_depth = curr.n_depth
            if self.testLeaf(curr) is True: # curr is a leaf node
                if curr.n_depth < Params.maxHeight:
                    remainingEps = sum(budget_c[curr.n_depth+1:])
                    curr.n_count = self.getCount(curr, remainingEps)
                nleaf += 1
                curr.n_isLeaf = True
                leaf_li.append(curr)
                
            else: # curr needs to split
                curr.n_budget -= 1
                tmp = self.getCoordinates(curr)
                if tmp is False: # if split fails
                    stack.append(curr)
                    continue
                nw_node, ne_node, sw_node, se_node = KNode(),KNode(),KNode(),KNode() # create sub-nodes
                split_prm, split_sec1, split_sec2, nw_node.n_data, ne_node.n_data, sw_node.n_data, se_node.n_data = tmp

                nw_node.n_box = (curr.n_box[0], split_sec1)
                ne_node.n_box = (split_sec1, split_prm)
                sw_node.n_box = (split_prm, split_sec2)
                se_node.n_box = (split_sec2, curr.n_box[1])
 
                for sub_node in [nw_node, ne_node, sw_node, se_node]:
                    sub_node.n_depth = curr.n_depth + 1
                    sub_node.n_count = self.getCount(sub_node, budget_c[sub_node.n_depth])
                    sub_node.n_budget = curr.n_budget
                    stack.append(sub_node)
                    tree.append(sub_node)
                curr.n_data = None
                curr.nw, curr.ne, curr.sw, curr.se = nw_node, ne_node, sw_node, se_node
                
        # end of while
        logging.debug("number of leaves: %d" % nleaf)
        logging.debug("max depth: %d" % max_depth)
        
        ## convert hilbert values in leaf nodes to real coordinates and update bounding box
        logging.debug('decoding and updating bounding box...')
        for leaf in leaf_li:
            bbox = np.array([[1000.0,1000.0],[-1000.0,-1000.0]],dtype='float64')
            for hvalue in leaf.n_data:
                hx,hy = self.h_decode(int(hvalue),RES)
                x,y = self.get_Rcoord(hx,hy,RES)
                bbox[0,0] = x if x < bbox[0,0] else bbox[0,0]
                bbox[1,0] = x if x > bbox[1,0] else bbox[1,0]
                bbox[0,1] = y if y < bbox[0,1] else bbox[0,1]
                bbox[1,1] = y if y > bbox[1,1] else bbox[1,1]
            leaf.n_box = bbox
        
        ## update bounding box bottom-up
        tree = sorted(tree,cmp=self.cmp_node)
        logging.debug('updating box for each node in the tree...')
        for node in tree:
            if node.n_data is None:
                node.n_box = np.zeros((2,2))
                node.n_box[0,0] = min(node.ne.n_box[0,0],node.nw.n_box[0,0],node.se.n_box[0,0],node.sw.n_box[0,0])
                node.n_box[0,1] = min(node.ne.n_box[0,1],node.nw.n_box[0,1],node.se.n_box[0,1],node.sw.n_box[0,1])
                node.n_box[1,0] = max(node.ne.n_box[1,0],node.nw.n_box[1,0],node.se.n_box[1,0],node.sw.n_box[1,0])
                node.n_box[1,1] = max(node.ne.n_box[1,1],node.nw.n_box[1,1],node.se.n_box[1,1],node.sw.n_box[1,1])
        
        
    def cmp_node(self,node1,node2):
        # reverse order
        return int(node2.n_depth-node1.n_depth)
        
    def getCoordinates(self, curr):
        budget_s = self.getSplitBudget()
        _data = curr.n_data
        _ndata = len(_data)
        split_1 = self.getSplit(_data, curr.n_box[0], curr.n_box[1], budget_s[curr.n_depth]/2)
        pos_1 = np.searchsorted(_data, split_1)
        if pos_1 == 0 or pos_1 == _ndata:
            return False
        data_1 = _data[:pos_1]
        data_2 = _data[pos_1:]
        split_sec1 = self.getSplit(data_1, curr.n_box[0], split_1, budget_s[curr.n_depth]/2)
        split_sec2 = self.getSplit(data_2, split_1, curr.n_box[1], budget_s[curr.n_depth]/2)
        pos_sec1 = np.searchsorted(data_1, split_sec1)
        pos_sec2 = np.searchsorted(data_2, split_sec2)
            
        if (pos_sec1 == 0 or pos_sec1 == len(data_1) or pos_sec2 == 0 or pos_sec2 == len(data_2)):
            return False
        nw_data, ne_data, sw_data, se_data = data_1[:pos_sec1], data_1[pos_sec1:], data_2[:pos_sec2], data_2[pos_sec2:]
        return split_1, split_sec1, split_sec2, nw_data, ne_data, sw_data, se_data
        
        
            