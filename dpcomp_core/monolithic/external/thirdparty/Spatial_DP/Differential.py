import numpy as np

class Differential(object):
    Delta = 10000 # delta inverse
    Beta = 2.0
    Two_appr = True # use 2-approximation for smooth sensitivity
    
    def __init__(self, prng):
        self.prng = prng
    
    def getUniform(self, lo, hi, size=1):
        return self.prng.uniform(lo,hi,size)
    
    def getNoise(self, sens, eps):
        """Get simple Laplacian noise"""
        return self.prng.laplace(0,sens/eps,1)[0]
    
    def getSplit_smooth(self, data_raw, left, right, eps, srt = 1):
        """Get noisy median, using smooth sensitivity (quadratic search or 2-approximation)"""
        if srt == 1: # no sampling
            data = data_raw
        else: # get sample first
            eps *= 1/(np.log(1+srt*(np.exp(1)-1)))
            n_raw = len(data_raw)
            idx = self.prng.permutation(n_raw)[0:int(n_raw*srt)]
            data = np.sort(data_raw[idx])
        
        n = len(data)
        if (n % 2  == 0):
            m1 = n/2 - 1
            m2 = n/2
        m = int(np.floor((n-1)/2))
        beta = 0.5*eps*(np.log(Differential.Delta))
        out_list = np.zeros(n+1)
        for k in range(n+1):
            damp = np.exp(-k*beta)
    #        in_list = np.zeros(k+2)
            if Differential.Two_appr is True: # use 2-approximation
                idx_big = m+k+1
                big = right if idx_big >= n else data[idx_big]
                idx_small = m-k-1
                small = left if idx_small < 0 else data[idx_small]
                in_max = big - small
    #        else: # use quadratic search
    #            for t in range(k+2):
    #                in_list[t] = eval(m+t)-eval(m+t-k-1)
    #            in_max = max(in_list)
            out_list[k] = damp * in_max
        
        sen = max(out_list)
        if (n % 2 == 1):
            split = data[m] + sen*2*self.prng.laplace()/eps
        else:
            split = (data[m1]+data[m2])/2 + sen*2*self.prng.laplace()/eps
            
        return split
    
    def getSplit_exp(self,data_raw,left,right,eps,srt = 1):
        """Get noisy median using exponential mechanism"""
        # 'data_raw' is the sorted input of n real numbers
        # 'left' and 'right' are the default boundaries
        if srt == 1 or len(data_raw)*srt <= 10:
            data = data_raw
        else: # get sample first
            eps *= 1/(np.log(1+srt*(np.exp(1)-1)))
            n_raw = len(data_raw)
            idx = self.prng.permutation(n_raw)[0:int(n_raw*srt)]
            data = np.sort(data_raw[idx])
        
        n = len(data)
        if (n % 2 == 1):
            rm = (n+1)/2 # rm is the rank of the median
        else:
            rm = n/2
        t = np.concatenate(([left],data,[right])) # input sequence with boundaries
        base = np.exp(-eps/Differential.Beta) # a constant
        
        prob_sum = np.zeros(n+2) # 'prob_sum' is a list of cumulative probability mass
        prob_sum[0] = 0.0
        
        for i in range(1,n+2): # populate 'prob_sum' for each of the n+1 buckets
            if i - 1 >= rm:
                prob_sum[i] = prob_sum[i-1] + (t[i]-t[i-1]) * (base**(i-1-rm))
            else:
                prob_sum[i] = prob_sum[i-1] + (t[i]-t[i-1]) * (base**(rm-i+1))
        
        rand = self.prng.uniform(0.0,1.0,1) # a random number in [0,1)
        idx = np.searchsorted(prob_sum, rand*prob_sum[n+1]) # the index of the bucket which 'rand' falls into
        split = self.prng.uniform(t[idx-1],t[idx],1) # pick a random number in the bucket as the split value

        return split[0]
    
    def getSplit_noisyMean(self, data_raw, left, right, eps):
        """Get noisy median using noisy mean"""
        noisy_count = len(data_raw) + self.getNoise(1,eps/2)
        noisy_sum = sum(data_raw) + self.getNoise(right-left,eps/2)
        
        return noisy_sum/noisy_count
    
    def getSplit_grid(self, data_raw, left, right, eps, unit):
        """Get noisy median using grid noisy counts, argument 'unit' is the
        number of cells, controlling the granularity"""
        n = len(data_raw)
        #left = np.floor(left)
        #right = np.ceil(right)
        no_cell = int(np.ceil((right-left)/unit))
        li = np.zeros(no_cell,dtype='float32')
        for i in range(n):
            cell = int(np.trunc(data_raw[i]-left)/unit)
            li[cell] += 1
        for i in range(no_cell):
            li[i] += self.getNoise(1,eps)
        total = sum(li)
        i = 0
        cur = li[0]
        while (cur < total/2):
            i += 1
            cur += li[i]
            if i == no_cell - 1 and cur < total/2:
                i = self.prng.randint(0,no_cell)
                break
        
        return self.prng.uniform(left+i*unit,left+(i+1)*unit,1) 
    