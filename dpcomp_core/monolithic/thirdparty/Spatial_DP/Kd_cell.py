import sys
import logging
import numpy as np
from Kd_pure import Kd_pure
from Params import Params
from collections import deque
from Differential import Differential
from KNode import KNode


class Kd_cell(Kd_pure):
    """ Kd tree based on syntatic data generation and a grid structure. See
    Y. Xiao, L. Xiong, and C. Yuan, Differentially private data release
    through multidimensional partitioning, in SDM Workshop, VLDB, 2010
    """
    def __init__(self, data, param):
        self.param = param
        self.differ = Differential(self.param.Seed)
        self.mapp = None
        self.root = KNode() 
        self.realData = data
        self.root.n_box = None
        self.root.n_budget = Params.maxHeight
    
    def getCountBudget(self):
        count_eps = self.param.Eps*0.5
        H = Params.maxHeight
        if self.param.geoBudget == 'none':
            return [count_eps/(H+1) for i in range(H+1)]
        elif self.param.geoBudget == 'aggressive':
            unit = count_eps/(2**(H+1)-1)
            return [unit*2**i for i in range(H+1)]
        elif self.param.geoBudget == 'quadratic':
            unit = count_eps * (np.sqrt(2)-1) / (2**(0.5*(H+1))-1)
            return [unit*2**(0.5*i) for i in range(H+1)]
        elif self.param.geoBudget == 'optimal':
            unit = count_eps * ((2**(1.0/3))-1) / (2**((1.0/3)*(H+1))-1)
            return [unit*2**((1.0/3)*i) for i in range(H+1)]
        elif self.param.geoBudget == 'quartic':
            unit = count_eps * ((2**(1.0/4))-1) / (2**((1.0/4)*(H+1))-1)
            return [unit*2**((1.0/4)*i) for i in range(H+1)]
        else:
            logging.error('No such geoBudget scheme')
            sys.exit(1)
    
    def synthetic_gen(self):
        """Apply a grid structure on the domain and perturb the count using half
        of the available privacy budget """
        logging.debug('generating synthetic map...')
        data = self.realData
        unit = Params.unitGrid
        x_min = np.floor(Params.LOW[0]/unit)*unit
        x_max = np.ceil(Params.HIGH[0]/unit)*unit
        y_min = np.floor(Params.LOW[1]/unit)*unit
        y_max = np.ceil(Params.HIGH[1]/unit)*unit
        
        x_CELL = int(np.rint((x_max-x_min)/unit))
        y_CELL = int(np.rint((y_max-y_min)/unit))
        
        self.root.n_box = np.array([[x_min,y_min],[x_max,y_max]])
        
        self.mapp = np.zeros((x_CELL,y_CELL))-1 ### initialize every cell with -1
        for i in range(Params.NDATA): ### populate the map
            point = data[:,i]
            cell_x = int(np.floor((point[0]-x_min)/unit))
            cell_y = int(np.floor((point[1]-y_min)/unit))
            if self.mapp[cell_x,cell_y] != -1:
                self.mapp[cell_x,cell_y] += 1
            else:
                self.mapp[cell_x,cell_y] = 1

        for i in range(x_CELL): ### perturb the counts
            for j in range(y_CELL):
                if self.mapp[i,j] != -1:
                    self.mapp[i,j] += np.rint(self.differ.getNoise(1,0.5*self.param.Eps))
                else:
                    self.mapp[i,j] = np.rint(self.differ.getNoise(1,0.5*self.param.Eps))
                # if noisy count is negative, ignore the noise and generate no points
                if self.mapp[i,j] < 0:
                    self.mapp[i,j] = 0

    def cell_setLeaf(self,curr):
        """ Throw away the counts based on the syntatic data """
        curr.n_count = 0
        return
                
    def testLeaf(self, curr):
        if (curr.n_count <= self.param.minPartSize) or (curr.n_depth == Params.maxHeight) or (self.uniform_test(curr,self.param.cellDistance)):
            return True
        return False
    
    def uniform_test(self, curr, distance):
        """ One of the stopping conditions: cell is uniform according to some threshold 'distance') """
        unit = Params.unitGrid
        x_min = int(np.rint((curr.n_box[0,0]-self.root.n_box[0,0])/unit))
        x_max = int(np.rint((curr.n_box[1,0]-self.root.n_box[0,0])/unit))
        y_min = int(np.rint((curr.n_box[0,1]-self.root.n_box[0,1])/unit))
        y_max = int(np.rint((curr.n_box[1,1]-self.root.n_box[0,1])/unit))
        data = self.mapp[x_min:x_max,y_min:y_max]
        total = np.sum(data)
        avg = total/((x_max-x_min)*(y_max-y_min))
        dist = np.sum(np.abs(data-avg))
        if dist > distance:
            return False
        else:
            return True
                
    def buildIndex(self):
        stack = deque()
        stack.append(self.root)
        nleaf = 0 # leaf counter
        max_depth = -1
        self.root.n_count = np.sum(self.mapp)
        while len(stack) > 0:
            curr = stack.popleft()
            if curr.n_depth > max_depth:
                max_depth = curr.n_depth
            if self.testLeaf(curr) is True: # curr is a leaf node
                nleaf += 1
                curr.n_isLeaf = True
                self.cell_setLeaf(curr)
            else: # curr needs to split
                curr.n_budget -= 1
                tmp = self.getCoordinates(curr)
                nw_node, ne_node, sw_node, se_node = KNode(),KNode(),KNode(),KNode() # create sub-nodes
                nw_coord, ne_coord, count_tmp = tmp
                x_nw, y_nw = nw_coord
                x_se, y_se = ne_coord
                
                nw_node.n_box = np.array([[curr.n_box[0,0],y_nw],[x_nw,curr.n_box[1,1]]])
                ne_node.n_box = np.array([[x_nw,y_se],[curr.n_box[1,0],curr.n_box[1,1]]])
                sw_node.n_box = np.array([[curr.n_box[0,0],curr.n_box[0,1]],[x_se,y_nw]])
                se_node.n_box = np.array([[x_se,curr.n_box[0,1]],[curr.n_box[1,0],y_se]])
                
                c_t = 0
                for sub_node in [nw_node, ne_node, sw_node, se_node]:
                    sub_node.n_depth = curr.n_depth + 1
                    sub_node.n_count = count_tmp[c_t]
                    sub_node.n_budget = curr.n_budget
                    stack.append(sub_node)
                    c_t += 1
                curr.nw, curr.ne, curr.sw, curr.se = nw_node, ne_node, sw_node, se_node
                
        # end of while
        logging.debug("number of leaves: %d" % nleaf)
        logging.debug("max depth: %d" % max_depth)
        
    def getCoordinates(self, curr):
        dim_1 = curr.n_depth % Params.NDIM # primary split dimension
        UNIT = Params.unitGrid
        x_min = int(np.rint((curr.n_box[0,0]-self.root.n_box[0,0])/UNIT))
        x_max = int(np.rint((curr.n_box[1,0]-self.root.n_box[0,0])/UNIT))
        y_min = int(np.rint((curr.n_box[0,1]-self.root.n_box[0,1])/UNIT))
        y_max = int(np.rint((curr.n_box[1,1]-self.root.n_box[0,1])/UNIT))
        
        total = np.sum(self.mapp[x_min:x_max,y_min:y_max])
        if dim_1 == 0:
            for i in range(x_max-x_min):
                if np.sum(self.mapp[x_min:x_min+i+1,y_min:y_max]) >= total/2:
                    break
            split_prm = (x_min+i+1)*UNIT+self.root.n_box[0,0]

            half_1 = np.sum(self.mapp[x_min:x_min+i+1,y_min:y_max])
            half_2 = np.sum(self.mapp[x_min+i+1:x_max,y_min:y_max])
            for j in range(y_max-y_min):
                if np.sum(self.mapp[x_min:x_min+i+1,y_min:y_min+j+1]) >= half_1/2:
                    break
            split_sec1 = self.root.n_box[0,1] + (y_min+j+1)*UNIT 
            n_sw = np.sum(self.mapp[x_min:x_min+i+1,y_min:y_min+j+1])
            n_nw = np.sum(self.mapp[x_min:x_min+i+1,y_min+j+1:y_max])
            for k in range(y_max-y_min):
                if np.sum(self.mapp[x_min+i+1:x_max,y_min:y_min+k+1]) >= half_2/2:
                    break
            split_sec2 = self.root.n_box[0,1] + (y_min+k+1)*UNIT
            n_se = np.sum(self.mapp[x_min+i+1:x_max,y_min:y_min+k+1])
            n_ne = np.sum(self.mapp[x_min+i+1:x_max,y_min+k+1:y_max])
            return (split_prm, split_sec1), (split_prm, split_sec2), (n_nw,n_ne,n_sw,n_se)
        
        else:
            for i in range(y_max-y_min):
                if np.sum(self.mapp[x_min:x_max,y_min:y_min+i+1]) >= total/2:
                    break
            split_prm = self.root.n_box[0,1] + (y_min+i+1)*UNIT

            half_1 = np.sum(self.mapp[x_min:x_max,y_min:y_min+i+1])
            half_2 = np.sum(self.mapp[x_min:x_max,y_min+i+1:y_max])
            for j in range(x_max-x_min):
                if np.sum(self.mapp[x_min:x_min+j+1,y_min:y_min+i+1]) >= half_1/2:
                    break
            split_sec1 = (x_min+j+1)*UNIT + self.root.n_box[0,0]
            n_sw = np.sum(self.mapp[x_min:x_min+j+1,y_min:y_min+i+1])
            n_se = np.sum(self.mapp[x_min+j+1:x_max,y_min:y_min+i+1])
            for k in range(x_max-x_min):
                if np.sum(self.mapp[x_min:x_min+k+1,y_min+i+1:y_max]) >= half_2/2:
                    break
            split_sec2 = (x_min+k+1)*UNIT + self.root.n_box[0,0]
            n_nw = np.sum(self.mapp[x_min:x_min+k+1,y_min+i+1:y_max])
            n_ne = np.sum(self.mapp[x_min+k+1:x_max,y_min+i+1:y_max])
            return (split_sec2, split_prm),(split_sec1, split_prm), (n_nw,n_ne,n_sw,n_se)

          
    def populate_synthetic_tree(self):
        """ Populate real data to the synthetic tree """
        logging.debug('populating synthetic tree...')
        a_data = self.realData
        ndata = a_data.shape[1]
        for i in range(ndata):
            ptx = a_data[0,i]
            pty = a_data[1,i]
            leaf = self.root.find_subnode(ptx,pty)
            leaf.n_count += 1
            
        # traverse the tree and update leaf counts
        stack = deque()
        stack.append(self.root)
        while len(stack) > 0:
            cur_node = stack.popleft()
            if cur_node.n_isLeaf is True: # leaf
                cur_node.n_count += self.differ.getNoise(1, 0.5*self.param.Eps)
            else:
                stack.append(cur_node.nw)
                stack.append(cur_node.ne)
                stack.append(cur_node.sw)
                stack.append(cur_node.se)
                
