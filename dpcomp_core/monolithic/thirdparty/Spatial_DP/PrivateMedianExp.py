import numpy as np
import time
from Differential import Differential
import dataGen

eps = 0.01 # epsilon for each level
dist = 'uniform' # see dataGen.py
LO = 0
HI = 2**26
NDATA = 2**20
NDIM = 1
srt = 0.01 # sampling rate
unit = 2**10
res_dir = 'output/'
seed_list = [1353,4564,6216]

def test_privateMedian():

        f = open(res_dir + 'privateMedian', 'w')
        f_t = open(res_dir + 'privateMedian-time', 'w')
        data = np.sort(dataGen.data_gen(dist, NDIM, LO, HI, NDATA)).flatten()
        n = len(data)

        for i in range(10):
            print 'level ' + `i`
            container = np.zeros(6)
            container_t = np.zeros(6)
            for seed in seed_list:
                perturber = Differential(seed)
                for j in range(2**i):
                    c_data = data[n*j/2**i:n*(j+1)/2**i]
                    c_len = len(c_data)

                    # exponential mechanism
                    start = time.clock()
                    em = perturber.getSplit_exp(c_data, c_data[0], c_data[-1], eps, 1)
                    end = time.clock()
                    container_t[0] += end-start
                    # smooth sensitivity (2-approx)
                    start = time.clock()
                    ls = perturber.getSplit_smooth(c_data, c_data[0], c_data[-1], eps, 1)
                    end = time.clock()
                    container_t[1] += end-start
                    # exponential mechanism sampling
                    start = time.clock()
                    em_samp = perturber.getSplit_exp(c_data, c_data[0], c_data[-1], eps, srt)
                    end = time.clock()
                    container_t[2] += end-start
                    # smooth sensitivity sampling
                    start = time.clock()
                    ls_samp = perturber.getSplit_smooth(c_data, c_data[0], c_data[-1], eps, srt)
                    end = time.clock()
                    container_t[3] += end-start
                    # noisy mean approximation
                    start = time.clock()
                    nm = perturber.getSplit_noisyMean(c_data, c_data[0], c_data[-1], eps)
                    end = time.clock()
                    container_t[4] += end-start
                    # noisy grid approximation
                    start = time.clock()
                    ng = perturber.getSplit_grid(c_data, c_data[0], c_data[-1], eps, unit)
                    end = time.clock()
                    container_t[5] += end-start

                    res = [em, ls, em_samp, ls_samp, nm, ng]
                    for k in range(6):
                        if res[k] >= c_data[-1] or res[k] <= c_data[0]:
                            container[k] += 1.0
                        else:
                            r_k = np.searchsorted(c_data,res[k])
                            r_m = float(c_len)/2
                            container[k] += abs(r_m-r_k)/r_m   
                # end of j loop
            for k in range(6):
                f.write(`container[k]/(2**i*len(seed_list))` + ' ')
            f.write('\n')
            for k in range(6):
                f_t.write(`container_t[k]/(2**i*len(seed_list))` + ' ')
            f_t.write('\n')
        # end of i
        f.close()
        f_t.close()

        
if __name__ == '__main__':
    print time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime()) + "  START"
    test_privateMedian()
    print time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime()) + "  END"


    
            