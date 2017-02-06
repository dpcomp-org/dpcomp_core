# DPComp Core
[DPComp.org](https://www.dpcomp.org/) is a web-based tool designed to help both practitioners and researchers assess the accuracy of state-of-the-art differentially private algorithms based on [DPBench](#dpbench).

This repository contains datasets, workloads, and algorithms used in DPBench, and is supporting core functionalities of dpcomp.org. With this dpcomp_core, a user could reproduce previous evalutations, compare provided algorithms with new data, or evaluate new algorithms. 

References to supporting paper are [here](#ref).
## DPComp Core Setup

### Example Environment

The following environment variables must be set.

```bash
export DPCOMP_CORE=$HOME/Documents/dpcomp_core
export PYTHON_HOME=$HOME/virtualenvs/PyDpcomp
export PYTHONPATH=$PYTHONPATH:$DPCOMP_CORE
export DPCOMP_LOG_PATH=$HOME/logs
export DPCOMP_LOG_LEVEL=DEBUG
```

Once initialization has been run, the virtual environment can be restored with
the following command.

```bash
source $PYTHON_HOME/bin/activate
```

### Initialization

Be sure to setup the environment (describe above) first. You will need to install 
several packages. The following commands should work for debian systems.

```bash
sudo apt-get install python-virtualenv gfortran liblapack-dev libblas-dev 
sudo apt-get install libpq-dev python-dev libncurses5-dev swig
```

Next, create a virtual environment for python by entering the commands below.

```bash
mkdir $DPCOMP_LOG_PATH
virtualenv $PYTHON_HOME
source $PYTHON_HOME/bin/activate
cd $DPCOMP_CORE
pip install -r resources/requirements.txt
```

Finally, after instantiating the virtualenv, compile the C libraries as follows.

```bash
cd $DPCOMP_CORE/dpcomp_core/algorithm
./setup.sh
```


## Testing

Execute the following in the base of the repository.

```bash
cd $DPCOMP_CORE
nosetests
```

### A specific module

```bash
nosetests test.system.test_experiment:TestExperiment
```

## Examples 
We provide some examples to start with.

To run a single algorithm, refer to `examples/algorithm_execution.py`.
```bash
cd $DPCOMP_CORE
$ python examples/algorithm_execution.py
Per Query Average Absolute Error: 41.4143661792
```


To run multiple experiment configuration, refer to `examples/simple_workflow.py`.
```bash
$ python examples/simple_workflow.py
[["{'error_payload': {'TypeI.L1': 0.081073246344863972, 'TypeI.L2': 0.0061553031454959529, 'TypeI.Linf': 0.26251196948550681}, 'key': '44299e07f79cdc0c7481a927', 'hash': '44299e07f79cdc0c7481a92740f70bad2cf97f4b',...
```
The output of this example script is experiment result in a json-like format. Query errors are stored with entry `error_payload`.


To run your own algorithm, refer to `examples/custom_algorithm.py`.
```bash
$ python examples/custom_algorithm.py
[["{'error_payload': {'TypeI.L1': 0.081073246344863972, 'TypeI.L2': 0.0061553031454959529, 'TypeI.Linf': 0.26251196948550681}, 'key': '44299e07f79cdc0c7481a927', 'hash': '44299e07f79cdc0c7481a92740f70bad2cf97f4b',...
```
This example script describes and runs a dummy custom algorithm. The output is similar as previous exmaple.

## List of algorithms 
|Canonical name| Additional aliases| Reference | invocation (omitting the `dpcomp_core.algorithm` prefix) |Implementation|
| ------------- |:-------------:| -----:|:---------:|:---:|
| Identity    | - |[C. Dwork, F. McSherry, K. Nissim, and A. Smith. Calibrating noise to sensitivity in private data analysis. TCC, 2006.](http://dl.acm.org/citation.cfm?id=2180305) |`identity.identity_engine()`| DPComp team|
|Privelet    | - | [ X. Xiao, G. Wang, and J. Gehrke. Differential privacy via wavelet transforms. ICDE, 2010.](http://dl.acm.org/citation.cfm?id=2007020) | `privelet.privelet_engine()` for 1D `privelet2D.privelet2D_engine()` for 2D|DPComp team |
|H   | Hierarchical | [M. Hay,V. Rastogi,G. Miklau, and D. Suciu. Boosting the accuracy of differentially private histograms through consistency. PVLDB, 2010.](http://dl.acm.org/citation.cfm?id=1920970)  | `HB.H2_engine()`(only 1D)| DPComp team|
|HB    | - |  [W. Qardaji, W. Yang,and N. Li. Understanding hierarchical methods for differentially private histograms. PVLDB, 2013.](http://dl.acm.org/citation.cfm?id=2556576) |`HB.HB_engine()` for 1D `HB2D.HB2D_engine()` for 2D|DPComp team |
|Greedy H    | greedyH | [C. Li, M. Hay, and G. Miklau. A data- and workload-aware algorithm for range queries under differential privacy. PVLDB, 2014.](http://dl.acm.org/citation.cfm?id=2732271)  |`dawa.greedyH_only_engine()` (only 1D) |DPComp team |
|Uniform    | UniformNoisy |-|` uniform.uniform_noisy_engine()`   |DPComp team |
|MWEM    | - |  [M. Hardt, K. Ligett, and F. McSherry. A simple and practical algorithm for differentially private data release. NIPS, 2012.](http://dl.acm.org/citation.cfm?id=2999325.2999396) |`mwemND.mwemND_engine()` |DPComp team |
|MWEM*    | MWEM_ADP | [M. Hay, A. Machanavajjhala, G. Miklau, Y. Chen, and D. Zhang. Principled evaluation of differentially private algorithms using DPBench. SIGMOD, 2016](http://dl.acm.org/citation.cfm?id=2882931) |`mwemND.mwemND_adaptive_engine()` | DPComp team|
|AHP    | - |  [X. Zhang, R. Chen, J. Xu, X. Meng, and Y. Xie. Towards accurate histogram publication under differential privacy. ICDM, 2014.](http://epubs.siam.org/doi/abs/10.1137/1.9781611973440.68) |`ahp.ahpND_engine()` | DPComp team|
|AHP*    | AHP_ADP |  [M. Hay, A. Machanavajjhala, G. Miklau, Y. Chen, and D. Zhang. Principled evaluation of differentially private algorithms using DPBench. SIGMOD, 2016](http://dl.acm.org/citation.cfm?id=2882931)  |`ahp.ahpND_adaptive_engine()` | DPComp team|
|DPCube    | - |  [Y. Xiao, L. Xiong, L. Fan, S. Goryczka, and H. Li. DPCube: Differentially private histogram release through multidimensional partitioning. Transactions of Data Privacy, 2014.](http://dl.acm.org/citation.cfm?id=2870615) |`DPcube1D.DPcube1D_engine()` for 1D `DPcube.DPcube_engine()` for 2D |DPComp team |
|DAWA    | - | [C. Li, M. Hay, and G. Miklau. A data- and workload-aware algorithm for range queries under differential privacy. PVLDB, 2014.](http://dl.acm.org/citation.cfm?id=2732271)  |`dawa.dawa_engine()` for 1D `dawa.dawa2D_engine()` for 2D |DPComp team |
|QuadTree    | - |  [G. Cormode, M. Procopiuc, E. Shen, D. Srivastava, and T. Yu. Differentially private spatial decompositions. ICDE, 2012.](http://dl.acm.org/citation.cfm?id=2310433) | `QuadTree.QuadTree_engine()` (only 2D)| DPComp team|
|UGrid    | UG | [W. Qardaji, W. Yang, and N. Li. Differentially private grids for geospatial data. ICDE, 2013.](http://dl.acm.org/citation.cfm?id=2510649.2511274) | `UG.UG_engine()`  (only 2D)|DPComp team |
|AGrid    | AG |[W. Qardaji, W. Yang, and N. Li. Differentially private grids for geospatial data. ICDE, 2013.](http://dl.acm.org/citation.cfm?id=2510649.2511274)| `AG.AG_engine()`  (only 2D) |DPComp team|
|PHP   | - | [G. Ács ,C .Castelluccia ,and R. Chen. Differentially private histogram publishing through lossy compression. ICDM, 2012.](http://ieeexplore.ieee.org/document/6413718/)| `thirdparty.php_engine()` (only 1D) |Authors of original paper ([Link to code](https://www.crysys.hu/~acs/misc/src/histogram_sanitizer-20140408.zip)) |
|EFPA    | - |[G. Ács ,C .Castelluccia ,and R. Chen. Differentially private histogram publishing through lossy compression. ICDM, 2012.](http://ieeexplore.ieee.org/document/6413718/) |`thirdparty.efpa_engine()`(only 1D) |Authors of original paper ([Link to code](https://www.crysys.hu/~acs/misc/src/histogram_sanitizer-20140408.zip)) |
|StructureFirst   | SF |[J. Xu, Z. Zhang, X. Xiao, Y. Yang, G. Yu, and M. Winslett. Differentially private histogram publication. VLDB, 2013.](http://dl.acm.org/citation.cfm?id=2581852&CFID=877817809&CFTOKEN=72173205)|  `thirdparty.StructureFirst_engine()` (only 1D) |Authors of original paper[ (Link to code)](http://faculty.neu.edu.cn/ise/xujia/home/code.zip) |


## <a name="ref"></a> Supporting publications
* <a name="dpbench"></a>[Principled Evaluation of Differentially Private Algorithms using DPBench](http://dl.acm.org/citation.cfm?id=2882931)
    Michael Hay, Ashwin Machanavajjhala, Gerome Miklau, Yan Chen, and Dan Zhang. 
    ACM Conference on Management of Data (SIGMOD) 2016 
* [Exploring Privacy-Accuracy Tradeoffs using DPCOMP](http://dl.acm.org/citation.cfm?id=2899387)
    Michael Hay, Ashwin Machanavajjhala, Gerome Miklau, Yan Chen, Dan Zhang, and George Bissias. 
    Demonstration, ACM Conference on Management of Data (SIGMOD) 2016
