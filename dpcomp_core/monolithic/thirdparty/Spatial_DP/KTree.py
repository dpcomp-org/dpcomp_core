import numpy as np
import logging
from KNode import KNode
from collections import deque
from Params import Params
from Differential import Differential

class KTree(object):
    """Generic tree template"""

    def __init__(self, data, param):
        self.param = param
        self.differ = Differential(self.param.prng)
        ### initialize the root
        self.root = KNode()
        self.root.n_data = data
        self.root.n_box = np.array([Params.LOW,Params.HIGH])
        self.root.n_budget = Params.maxHeight
        
    def getSplitBudget(self):
        """return a list of h budget values for split"""
        raise NotImplementedError
    
    def getCountBudget(self):
        """return a list of (h+1) budget values for noisy count"""
        raise NotImplementedError
    
    def getNoisyMedian(self, array, left, right, epsilon):
        """return the split value of an array"""
        raise NotImplementedError
    
    def getCoordinates(self, curr):
        """
        return the coordinate of lower-right point of the NW sub-node
        and the upper-left point of the SW sub-node and the data points
        in the four subnodes, i.e.
        return (x_nw,y_nw),(x_se,y_se), nw_data, ne_data, sw_data, se_data
        """
        raise NotImplementedError

    def getSplit(self,array,left,right,epsilon):
        """
        return the split point given an array, may be data-independent or
        true median or noisy median, depending on the type of the tree
        """
        raise NotImplementedError
    
    def getCount(self, curr, epsilon):
        """ return true count or noisy count of a node, depending on epsilon"""
        if curr.n_data is None:
            count = 0
        else:
            count = curr.n_data.shape[1]
        if epsilon < 10**(-6):
            return count
        else:
            return count + self.differ.getNoise(1,epsilon)
    
    def testLeaf(self, curr):
        """ test whether a node should be a leaf node """
        if (curr.n_depth == Params.maxHeight) or \
            (curr.n_budget <= 0) or \
            (curr.n_data is None or curr.n_data.shape[1] == 0) or \
            (curr.n_count <= self.param.minPartSize):
            return True
        return False
    
    def cell_setLeaf(self, curr):
        """ will be overrided in kd_cell """
        return
             
    def buildIndex(self):
        """ Function to build the tree structure, fanout = 4 by default for spatial (2D) data """
        budget_c = self.getCountBudget()
        self.root.n_count = self.getCount(self.root,budget_c[0]) ### add noisy count to root
        stack = deque()
        stack.append(self.root)
        nleaf = 0 ### leaf counter
        max_depth = -1
        ### main loop 
        while len(stack) > 0:
            curr = stack.popleft()
            if curr.n_depth > max_depth:
                max_depth = curr.n_depth
                
            if self.testLeaf(curr) is True: ### curr is a leaf node
                if curr.n_depth < Params.maxHeight: ### if a node ends up earlier than maxHeight, it should be able to use the remaining count budget
                    remainingEps = sum(budget_c[curr.n_depth+1:])
                    curr.n_count = self.getCount(curr, remainingEps)
                nleaf += 1
                curr.n_isLeaf = True
                self.cell_setLeaf(curr)
                
            else: ### curr needs to split
                curr.n_budget -= 1 ### some budget will be used regardless the split is successful or not
                tmp = self.getCoordinates(curr)
                nw_node, ne_node, sw_node, se_node = KNode(),KNode(),KNode(),KNode() # create sub-nodes
                nw_coord, ne_coord, nw_node.n_data, ne_node.n_data, sw_node.n_data, se_node.n_data = tmp
                x_nw, y_nw = nw_coord
                x_se, y_se = ne_coord
                ### update bounding box, depth, count, budget for the four subnodes
                nw_node.n_box = np.array([[curr.n_box[0,0],y_nw],[x_nw,curr.n_box[1,1]]])
                ne_node.n_box = np.array([[x_nw,y_se],[curr.n_box[1,0],curr.n_box[1,1]]])
                sw_node.n_box = np.array([[curr.n_box[0,0],curr.n_box[0,1]],[x_se,y_nw]])
                se_node.n_box = np.array([[x_se,curr.n_box[0,1]],[curr.n_box[1,0],y_se]])

 
                for sub_node in [nw_node, ne_node, sw_node, se_node]:
                    sub_node.n_depth = curr.n_depth + 1
                    sub_node.n_count = self.getCount(sub_node, budget_c[sub_node.n_depth])
                    sub_node.n_budget = curr.n_budget
                    stack.append(sub_node)

                curr.n_data = None ### do not need the data points coordinates now
                curr.nw, curr.ne, curr.sw, curr.se = nw_node, ne_node, sw_node, se_node
        # end of while

        logging.debug("number of leaves: %d" % nleaf)
        logging.debug("max depth: %d" % max_depth)
    
    def intersect(self, hrect, query):
        """
        checks if the hyper-rectangle intersects with the
        hyper-rectangle defined by the query in every dimension
    
        """
	

        bool_m1 = query[0,:] >= hrect[1,:]
        bool_m2 = query[1,:] <= hrect[0,:]
        bool_m = np.logical_or(bool_m1, bool_m2)
        if np.any(bool_m):
            return False
        else:
            return True
        
    def rangeCount(self, query):
        """
        Query answering function. Find the number of data points within a query rectangle.
        """
        stack = deque()
        stack.append(self.root)
        count = 0.0
        ### Below are three variables recording the number of 1) whole leaf 2) partial leaf 3) whole internal node, 
        ### respectively, which contribute to the query answer. For debug purpose only.
        l_whole, l_part, i_whole = 0, 0, 0 
        
        while len(stack) > 0:
            curr = stack.popleft()
            _box = curr.n_box
            if curr.n_isLeaf is True:
                frac = 1
                if self.intersect(_box,query):
                    for i in range(_box.shape[1]):
                        if _box[1,i] == _box[0,i]:
                            frac *= 1
                        else:
                            frac *= (min(query[1,i],_box[1,i])-max(query[0,i],_box[0,i])) / (_box[1,i]-_box[0,i])
                    count += curr.n_count*frac
                    if 1.0 - frac < 10**(-6):
                        l_whole += 1
                    else:
                        l_part += 1

            else: ### if not leaf
                bool_matrix = np.zeros((2,query.shape[1]))
                bool_matrix[0,:] = query[0,:] <= _box[0,:]
                bool_matrix[1,:] = query[1,:] >= _box[1,:]
    
                if np.all(bool_matrix) and self.param.useLeafOnly is False: ### if query range contains node range
                    count += curr.n_count
                    i_whole += 1
                else:
                    if self.intersect(curr.nw.n_box, query):
                        stack.append(curr.nw)
                    if self.intersect(curr.ne.n_box, query):
                        stack.append(curr.ne)
                    if self.intersect(curr.sw.n_box, query):
                        stack.append(curr.sw)
                    if self.intersect(curr.se.n_box, query):
                        stack.append(curr.se)

        return float(count) #, i_whole, l_whole, l_part
    
    def adjustConsistency(self):
        """ 
        Post processing for uniform noise across levels. Due to 
        Michael Hay, Vibhor Rastogi, Gerome Miklau, Dan Suciu, 
        Boosting the Accuracy of Differentially-Private Histograms Through Consistency,
        VLDB 2010
        """
        logging.debug('adjusting consistency...')
        ### upward pass
        self.root.get_z()
        ### downward pass
        queue = deque()
        queue.append(self.root)
        while (len(queue) > 0):
            curr = queue.popleft()
            if curr.n_isLeaf is False:
                adjust = (curr.n_count - curr.nw.n_count - curr.ne.n_count - curr.sw.n_count - curr.se.n_count)/4.0
                for subnode in [curr.nw, curr.ne, curr.sw, curr.se]:
                    subnode.n_count += adjust
                    queue.append(subnode)
        
    def postProcessing(self):
        """ 
        Post processing for general noise distribution across levels. Due to
        G. Cormode, M. Procopiuc, E. Shen, D. Srivastava and T. Yu, 
        Differentially Private Spatial Decompositions, ICDE 2012.
        """
        logging.debug("post-processing...")
        budget = self.getCountBudget() ### count budget for h+1 levels
        H = Params.maxHeight
        ### Phase 1 (top-down)
        queue = deque()
        self.root.n_count *= budget[self.root.n_depth]**2
        queue.append(self.root)
        while (len(queue) > 0):
            curr = queue.popleft()
            if curr.n_isLeaf is False:
                for subnode in [curr.nw, curr.ne, curr.sw, curr.se]:
                    subnode.n_count = curr.n_count + subnode.n_count*(budget[subnode.n_depth]**2)
                    queue.append(subnode)
        ### Phase 2 (bottom-up)
        self.root.update_count()
        ### Phase 3 (top-down)
        queue = deque()
        E_root = 0
        for i in range(H+1):
            E_root += 4**i*budget[H-i]*budget[H-i]
        self.root.n_count /= E_root
        self.root.n_F = 0
        queue.append(self.root)
        while (len(queue) > 0):
            curr = queue.popleft()
            if curr.n_isLeaf is False:
                h = H - curr.n_depth - 1 ### height of curr's children
                E_h = 0
                for i in range(h+1):
                    E_h += 4**i*budget[H-i]*budget[H-i]
                for subnode in [curr.nw, curr.ne, curr.sw, curr.se]:
                    subnode.n_F = curr.n_F + curr.n_count*(budget[curr.n_depth]**2)
                    subnode.n_count = (subnode.n_count - 4**h*subnode.n_F)/E_h
                    queue.append(subnode)
        
    def pruning(self):
        """
        If the tree is grown without the stopping condition of minLeafSize, prune it here after post processing
        """
        logging.debug("pruning...")
        queue = deque()
        queue.append(self.root)
        while (len(queue) > 0):
            curr = queue.popleft()
            if curr.n_isLeaf is False:
                if curr.n_count <= self.param.minPartSize:
                    curr.n_isLeaf = True
                else:
                    queue.append(curr.nw)
                    queue.append(curr.ne)
                    queue.append(curr.sw)
                    queue.append(curr.se)
