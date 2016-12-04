import numpy as np
import sys
## parameters for fractal distribution
FRAC = 0.8
NLEV = 16

def data_gen(dist, ndim, lo, hi, ndata):
    """
    Generate four types of data: uniform, normal, two-normal, gamma
    Since the distributions cannot be bounded (except uniform),
    re-sample is needed for those out-of-bound points
    """
    rng = hi - lo
    if dist == 'uniform':
        return rng * np.random.rand(ndim,ndata)
    elif dist == 'normal':
        ret = np.empty((ndim,ndata))
        sd = 0.5*rng/3
        loc = 0.5*rng
        for i in range(ndim):
            samp = np.random.normal(loc,sd,ndata)
            for j in range(len(samp)):
                if samp[j] < lo or samp[j] > hi:
                    samp[j] = samp[j] % rng + lo

            ret[i,:] = samp
        return ret
    elif dist == 'double-normal':
        ret = np.empty((ndim,ndata))
        sd = 0.25*rng/3
        loc1 = 0.3*rng
        loc2 = 0.7*rng
        for i in range(ndim):
            samp1 = np.random.normal(loc1,sd,ndata/2)
            for j in range(len(samp1)):
                if samp1[j] < lo or samp1[j] > hi:
                    samp[j] = samp[j] % rng + lo
            samp2 = np.random.normal(loc2,sd,ndata/2)
            for j in range(len(samp2)):
                if samp2[j] < lo or samp2[j] > hi:
                    samp[j] = samp[j] % rng + lo

            ret[i,:] = np.concatenate((samp1,samp2))
        return ret
    elif dist == 'gamma':
        ret = np.empty((ndim,ndata))
        for i in range(ndim):
            samp = rng/35*np.random.gamma(5,2,ndata)
            for j in range(len(samp)):
                if samp[j] < lo or samp[j] > hi:
                    samp[j] = samp[j] % rng + lo

            ret[i,:] = samp
        return ret
    elif dist == 'fractal':
        p = FRAC
        h = NLEV
        ret = np.zeros((ndim,ndata))
        for dim in range(ndim):
            array = np.zeros(2**h)
            array[0] = p
            array[1] = 1-p
            for i in range(2,h+1,1):
                tmp_array = array.copy()
                for j in range(2**i):

                    if j%2 == 0:
                        array[j] = tmp_array[j/2]*p
                    else:
                        array[j] = tmp_array[(j-1)/2]*(1-p)
            array *= ndata
            array = np.rint(array)
            prev = 0
            unit = rng*0.9/float(2**h)
            for k in range(2**h):
                now = prev + int(array[k])
                ret[dim,prev:now] = np.random.uniform(unit*k,unit*(k+1),array[k])
                prev = now
            idx = np.random.permutation(ndata)
            ret[dim,:] = ret[dim,idx]

        return ret
    elif dist == 'zipf':
        ret = np.empty((ndim,ndata))
        for i in range(ndim):
            samp = np.random.zipf(2,ndata)
            for j in range(len(samp)):
                samp[j] = hash(`samp[j]`+'magic') % rng

            ret[i,:] = samp
        return ret

    else:
        sys.exit("distribution not supported")