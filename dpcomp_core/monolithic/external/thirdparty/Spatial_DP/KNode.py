from Params import Params

class KNode(object):
    """ generic tree node class """
    def __init__(self):
        self.n_data = None # list of data points
        self.n_box = None # 2 by 2 matrix [[x_min,y_min],[x_max,y_max]]
        self.nw = self.ne = self.sw = self.se = None
        self.n_count = 0 # noisy count of this node
        self.n_depth = 0
        self.n_budget = 0
        self.n_failSplit = False
        self.n_isLeaf = False 
        self.n_F = 0 # used in post-processing
    
    def get_z(self):
        if self.n_isLeaf is True:
            return
        else:
            self.nw.get_z()
            self.ne.get_z()
            self.sw.get_z()
            self.se.get_z()
            l = Params.maxHeight - self.n_depth
            self.n_count = (4**l-4**(l-1))/float(4**l-1)*self.n_count + \
                    (4**(l-1)-1)/float(4**l-1)*(self.nw.n_count+ \
                    self.ne.n_count+self.sw.n_count+self.se.n_count)
    
    
    def update_count(self):
        if self.n_isLeaf is False:
            self.nw.update_count()
            self.ne.update_count()
            self.sw.update_count()
            self.se.update_count()
            self.n_count = self.nw.n_count + self.ne.n_count + self.sw.n_count + self.se.n_count
        
    
    def find_subnode(self,ptx,pty):
        if self.n_isLeaf is True:
            return self
        elif ptx <= self.nw.n_box[1,0] and pty >= self.nw.n_box[0,1]:
            return self.nw.find_subnode(ptx,pty)
        elif ptx >= self.ne.n_box[0,0] and pty >= self.ne.n_box[0,1]:
            return self.ne.find_subnode(ptx,pty)
        elif ptx <= self.sw.n_box[1,0] and pty <= self.sw.n_box[1,1]:
            return self.sw.find_subnode(ptx,pty)
        elif ptx >= self.se.n_box[0,0] and pty <= self.se.n_box[1,1]:
            return self.se.find_subnode(ptx,pty)
        