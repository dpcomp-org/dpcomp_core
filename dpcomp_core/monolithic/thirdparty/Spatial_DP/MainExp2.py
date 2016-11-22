import numpy as np
import time
import os
import multiprocessing as mult
import sys
import logging
from KExp import KExp
from Params import Params
import math

seedList = [2172,7818,1254,4455,3113] 
q_list = [(5.0,5.0)]
methodList = None
exp_name = None

    
def data_readin(domain,scale):
    """Read in spatial data and initialize global variables."""
    
    name = Params.dataset + str(domain) + "_" + str(scale)
    data = np.genfromtxt(name,unpack = True)
    Params.NDIM, Params.NDATA = data.shape[0], data.shape[1]
    Params.LOW, Params.HIGH = np.amin(data,axis=1), np.amax(data,axis=1)
    logging.debug(`data.shape`)
    logging.debug(`Params.LOW`)
    logging.debug(`Params.HIGH`)
    return data

def queryGen(queryShape, seed, random=False, x1=-116.915680, y1=37.000293, x2=-109.050173, y2=45.543541,domain=100):
    """Query generation. Each of which has at least one corner point in data populated areas.
    Due to the distribution of the spatial data set, we do not want to generate many queries in 
    the blank area. Hence the query generation function here is highly related to the Washington-NewMexico
    data we use here. x1,y1,x2,y2 are the inner boundaries of the two states respectively.
    You are encouraged to write your own query generation function depending on the dataset you use."""
    
#    logging.debug('Generating queries...')
#    np.random.seed(seed)
#    querylist = []
#    if random:
#        x_range = np.random.uniform(0.2,15,Params.nQuery/2)
#        y_range = np.random.uniform(0.2,15,Params.nQuery/2)
#    else:
#        x_range, y_range = queryShape[0], queryShape[1]
    
#    point_x = np.random.uniform(Params.LOW[0],x1,Params.nQuery/2)
#    point_y = np.random.uniform(y2,Params.HIGH[1],Params.nQuery/2)
#    x_low = point_x 
#    x_high = point_x + x_range
#    y_low = point_y - y_range
#    y_high = point_y 
#    for i in range(Params.nQuery/2):
#        querylist.append(np.array([[x_low[i],y_low[i]],[x_high[i],y_high[i]]]))

#    point_x = np.random.uniform(x2,Params.HIGH[0],Params.nQuery/2)
#    point_y = np.random.uniform(Params.LOW[1],y1,Params.nQuery/2)
#    x_low = point_x - x_range
#    x_high = point_x
#    y_low = point_y 
#    y_high = point_y + y_range
#    for i in range(Params.nQuery/2):
#        querylist.append(np.array([[x_low[i],y_low[i]],[x_high[i],y_high[i]]]))


    
    file = open("../../2D/" + str(domain) + "_2DRandomRangeWorkload_0","rb");
    lines = file.readlines();
    file.close();
    querylist = [];
    l = len(lines);
	
    for i in range(l):
	lines[i] = lines[i].decode('gbk');
	w = lines[i].split(" ");
	querylist.append(np.array([[int(w[0]),int(w[1])],[int(w[2]),int(w[3])]]));

    return querylist

def test_quadtreeOpt(queryShape,domain,scale):
    global methodList, exp_name
    exp_name = 'quadtreeOpt'
    methodList = ['Quad-opt']
    
    Params.maxHeight = int(math.log(domain))
    epsList = [1.0,0.1]
    data = data_readin(domain,scale)
    res_cube_abs = np.zeros((len(epsList),len(seedList),len(methodList)))
    res_cube_rel = np.zeros((len(epsList),len(seedList),len(methodList)))
    
    for j in range(len(seedList)):
        queryList = queryGen(queryShape, seedList[j],True,0,domain + 1,0,domain+1,domain)
        kexp = KExp(data, queryList)
        for i in range(len(epsList)):
            for k in range(len(methodList)):
                p = Params(seedList[j])
                p.Eps = epsList[i]
                if methodList[k] == 'Quad-baseline':
                    res_cube_abs[i,j,k], res_cube_rel[i,j,k] = kexp.run_Quad_baseline(p)
                elif methodList[k] == 'Quad-geo':
                    res_cube_abs[i,j,k], res_cube_rel[i,j,k] = kexp.run_Quad_geo(p)
                elif methodList[k] == 'Quad-post':
                    res_cube_abs[i,j,k], res_cube_rel[i,j,k] = kexp.run_Quad_post(p) 
                elif methodList[k] == 'Quad-opt':
                    print("Quad-opt running")
                    res_cube_abs[i,j,k], res_cube_rel[i,j,k] = kexp.run_Quad_opt(p)
                    print("Quad-opt done")
		else:
                    logging.error('No such index structure!')
                    sys.exit(1)
    
    print(res_cube_abs)
    res_abs_summary = np.average(res_cube_abs,axis=1)
    res_rel_summary = np.average(res_cube_rel,axis=1)
    print(res_abs_summary)
   
    file = open("output/twitter" + str(domain) + "_" + str(scale),'wb');
    for x in res_abs_summary:
	st = str(x[0]) + "\n";
	file.write(st.encode('gbk'));
    file.close();
    
 #   np.savetxt(Params.resdir+ 'twitter' + str(domain) + "_" + str(scale), res_abs_summary, fmt='%.4f')
 #   np.savetxt(Params.resdir+ 'twitter' + str(domain) + "_" + str(scale), res_rel_summary, fmt='%.4f')
    
        
def test_kdTrees(queryShape,domain,scale):
    global methodList, exp_name
    exp_name = 'kdTrees'
    methodList = ['hybrid']
    Params.maxHeight = int(math.log(domain))
#    Params.maxHeight = 10;
    epsList = [1.0,0.1]
    data = data_readin(domain,scale)
    res_cube_abs = np.zeros((len(epsList),len(seedList),len(methodList)))
    res_cube_rel = np.zeros((len(epsList),len(seedList),len(methodList)))
    
    for j in range(len(seedList)):
        queryList = queryGen(queryShape, seedList[j])
        kexp = KExp(data, queryList)
        for i in range(len(epsList)):
            for k in range(len(methodList)):
                p = Params(seedList[j])
                p.Eps = epsList[i]
                if methodList[k] == 'pure':
                    res_cube_abs[i,j,k], res_cube_rel[i,j,k] = kexp.run_Kd_pure(p)
                elif methodList[k] == 'true':
                    res_cube_abs[i,j,k], res_cube_rel[i,j,k] = kexp.run_Kd_true(p)
                elif methodList[k] == 'standard':
                    res_cube_abs[i,j,k], res_cube_rel[i,j,k] = kexp.run_Kd_standard(p)
                elif methodList[k] == 'hybrid':
		    print("Hybrid running");
                    res_cube_abs[i,j,k], res_cube_rel[i,j,k] = kexp.run_Kd_hybrid(p) 
		    print("Hybrid done");
                elif methodList[k] == 'noisymean':
                    res_cube_abs[i,j,k], res_cube_rel[i,j,k] = kexp.run_Kd_noisymean(p)
                elif methodList[k] == 'cell':
                    res_cube_abs[i,j,k], res_cube_rel[i,j,k] = kexp.run_Kd_cell(p)
                else:
                    logging.error('No such index structure!')
                    sys.exit(1)
			
		file = open("output/newhybrid" + str(domain) + "_" + str(scale),'ab');
        	st = str(p.Eps) + " " + str(res_cube_abs[i,j,k]) + "\n";
        	file.write(st.encode('gbk'));
    		file.close();
    
    res_abs_summary = np.average(res_cube_abs,axis=1)
    res_rel_summary = np.average(res_cube_rel,axis=1)

    file = open("output/newhybrid" + str(domain) + "_" + str(scale),'ab');
    for x in res_abs_summary:
        st = str(x[0]) + "\n";
        file.write(st.encode('gbk'));
    file.close();

#    np.savetxt(Params.resdir+exp_name+'_abs_'+`int(queryShape[0]*10)`+'_'+`int(queryShape[1]*10)`, res_abs_summary, fmt='%.4f')
#    np.savetxt(Params.resdir+exp_name+'_rel_'+`int(queryShape[0]*10)`+'_'+`int(queryShape[1]*10)`, res_rel_summary, fmt='%.4f')


def test_height(queryShape):
    heightList = [6,7,8,9,10]
    methodList = ['quad-opt', 'hybrid', 'cell','hilbert']
    data = data_readin()
    res_cube_abs = np.zeros((len(heightList),len(seedList),len(methodList)))
    res_cube_rel = np.zeros((len(heightList),len(seedList),len(methodList)))

    for j in range(len(seedList)):
        queryList = queryGen(queryShape, seedList[j])
        kexp = KExp(data, queryList)
        p = Params(seedList[j])
        for i in range(len(heightList)):
            Params.maxHeight = heightList[i]
            for k in range(len(methodList)):
                if methodList[k] == 'quad-opt':
                    res_cube_abs[i,j,k], res_cube_rel[i,j,k] = kexp.run_Quad_opt(p)
                elif methodList[k] == 'hybrid':
                    res_cube_abs[i,j,k], res_cube_rel[i,j,k] = kexp.run_Kd_hybrid(p)
                elif methodList[k] == 'cell':
                    res_cube_abs[i,j,k], res_cube_rel[i,j,k] = kexp.run_Kd_cell(p) 
                elif methodList[k] == 'hilbert':
                    res_cube_abs[i,j,k], res_cube_rel[i,j,k] = kexp.run_Hilbert(p)
                else:
                    logging.error('No such index structure!')
                    sys.exit(1)

    res_abs_summary = np.average(res_cube_abs,axis=1)
    res_rel_summary = np.average(res_cube_rel,axis=1)
    for str in ['abs','rel']:
        summary = eval('res_'+str+'_summary')
        outName = Params.resdir+'twitter_'+ str(domain) + str(scale)
        outFile = open(outName,'w')
        outFile.write('#; ' + '; '.join(methodList) + '\n')
        for i in range(len(heightList)):
            outFile.write(`heightList[i]`)
            for j in range(len(methodList)):
                outFile.write(' '+`summary[i,j]`)
            outFile.write('\n')
        outFile.close()


def createGnuData():
    """
    Post-processing output files to generate Gnuplot-friendly outcomes
    """
    epsList = [1.0]
    line = 0
    for eps in epsList:
        for type in ['abs','rel']:
            out = open(Params.resdir + exp_name + '_eps' + `int(eps*10)`+ '_' + type, 'w')
            out.write('#; ' + '; '.join(methodList) + '\n')
            q_num = 1
            for queryShape in q_list:
                fileName = Params.resdir + exp_name + '_' + type + '_' + `int(queryShape[0]*10)` + '_' + `int(queryShape[1]*10)`
#                try:
                thisfile = open(fileName, 'r')
#                except:
#                    sys.exit('no input result file!')
                out.write(`q_num` + ' ' + thisfile.readlines()[line])
                thisfile.close()
                q_num += 1
            out.close()
        line += 1
    
    for type in ['abs','rel']:
        for queryShape in q_list:
            fileName = Params.resdir + exp_name + '_' + type + '_' + `int(queryShape[0]*10)` + '_' + `int(queryShape[1]*10)`
            os.remove(fileName)


if __name__ == '__main__':
    
    args = sys.argv;
    logging.basicConfig(level=logging.DEBUG, filename='debug.log')
    logging.info(time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime()) + "  START") 
    
    ### Experiment 1: test quadtree optimizations ###
#    for q_shape in q_list:
#        test_quadtreeOpt(q_shape,int(args[1]),int(args[2]))
#    createGnuData()
    ### Experiment 2: test various kd-trees ###
    for q_shape in q_list:
        test_kdTrees(q_shape,int(args[1]),int(args[2]))
#    createGnuData()
#    ### Experiment 3: test the impact of max tree height ###
#    for q_shape in q_list:
#        test_height(q_shape)
    
    ######### run with multi-core support, number of cores should be at least len(q_list) #########    
#    pool = mult.Pool(processes=len(q_list))
#    pool.map(test_quadtreeOpt,q_list)
#    pool.close()
#    pool.join()
#
#    pool.map(test_kdTrees,q_list)
#    pool.close()
#    pool.join()

#    pool.map(test_height,q_list)
#    pool.close()
#    pool.join()
    ######### 
    
    logging.info(time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime()) + "  END") 
