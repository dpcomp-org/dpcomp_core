#Third party code

This directory contains code implemented by authors of original paper which introduced the algorithms. The algorithms have been incorporated into the repo, and the invocation interfaces are same as any other algorithm's. The interfaces are described in `__init__.py` of the current folder.

	Please don't run the code directly but instead call the python invocation indicated in the table below. 


|Canonical name| Additional aliases| Reference | Invocation (omitting the `dpcomp_core.monolithic` prefix) |Implementation|
| ------------- |:-------------:| -----:|:---------:|:---:|
|PHP   | - | [G. Ács ,C .Castelluccia ,and R. Chen. Differentially private histogram publishing through lossy compression. ICDM, 2012.](http://ieeexplore.ieee.org/document/6413718/)| `thirdparty.php_engine()` (only 1D) |Authors of original paper ([Link to code](https://www.crysys.hu/~acs/misc/src/histogram_sanitizer-20140408.zip)) |
|EFPA    | - |[G. Ács ,C .Castelluccia ,and R. Chen. Differentially private histogram publishing through lossy compression. ICDM, 2012.](http://ieeexplore.ieee.org/document/6413718/) |`thirdparty.efpa_engine()`(only 1D) |Authors of original paper ([Link to code](https://www.crysys.hu/~acs/misc/src/histogram_sanitizer-20140408.zip)) |
|StructureFirst   | SF |[J. Xu, Z. Zhang, X. Xiao, Y. Yang, G. Yu, and M. Winslett. Differentially private histogram publication. VLDB, 2013.](http://dl.acm.org/citation.cfm?id=2581852&CFID=877817809&CFTOKEN=72173205)|  `thirdparty.StructureFirst_engine()` (only 1D) |Authors of original paper[ (Link to code)](http://faculty.neu.edu.cn/ise/xujia/home/code.zip) |


