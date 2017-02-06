# Datasets

## One-dimensional data

    
|      Name     | Additional aliases  |           Data File                 |      Source |
|---------------|---------------------|-------------------------------------|-------------|           
| HEPTH         | -     |   `1D/HEPTH.n4096.npy`      | Arxiv High Energy Physics paper citation network<sup>[1](#dawadata)</sup>: describing number of citations for each paper (scale is not consistent to the source)|                                              
| ADULT    | -   |`1D/ADULTFRANK.n4096.npy` | [Adult Census Dataset](https://archive.ics.uci.edu/ml/datasets/Adult): describing the “capital loss” attribute of each person |                                   
| INCOME        | -     |`1D/INCOME.n4096.npy`         | IPUMS USA collected census microdata<sup>[1](#dawadata)</sup>: describing “personal income” attribute of person on the survey from 2001-2011|          
| MEDCOST       | -         |`1D/MEDCOST.n4096.npy`        | National home and hospice care 2007 survey data<sup>[1](#dawadata)</sup>: describing the personal medical expenses|
| NETTRACE      | -     | `1D/NETTRACE.n4096.npy`       | [Bipartite connection on an IP-level network trace collected at a major university](https://github.com/michaelghay/vldb2010data#nettrace): describing the number of external connections made by each internal host|                                              
| PATENT        | -      |`1D/PATENT.n4096.npy`         |  US patent dataset (from 1/1/1963 to 12/30/1999) maintained by the National Bureau of Economic Research<sup>[1](#dawadata)</sup>: describing the number of citations for each patent|                                             
| SEARCHLOGS    | SEARCH |`1D/SEARCHLOGS.n4096.npy`         | [Search query logs dataset](https://github.com/michaelghay/vldb2010data#search-logs): describing the frequency of search term “Obama” over time (from 2004 to 2010)|
| BIDS-FJ       | -      |`1D/bids_j.npy`       | [Kaggle competition testing dataset](https://www.kaggle.com/c/facebook-recruiting-iv-human-or-bot/data): describing the number of individual bids where “merchandise=jewelry” on each IP address|  
| BIDS-FM       | -     |`1D/bids_m.npy`       | [Kaggle competition testing dataset](https://www.kaggle.com/c/facebook-recruiting-iv-human-or-bot/data): describing the number of individual bids where “merchandise=mobile” on each IP address|  
| BIDS-ALL      | -     |`1D/bids.npy`         | [Kaggle competition testing dataset](https://www.kaggle.com/c/facebook-recruiting-iv-human-or-bot/data): describing the total number of individual bids on each IP address|
| MDSALARY      | MD-SAL    |`1D/GrossCompenMDSalary1.npy`         | [Maryland salary database (2012 state employee)](http://data.baltimoresun.com/salaries/state/cy2012/) : describing “YTD-gross-compensation” attribute|
| MDSALARY-FA   | MD-SAL-FA| `1D/GrossCompenMDSalary2_filtered.npy`        |[Maryland salary database (2012 state employee)](http://data.baltimoresun.com/salaries/state/cy2012/)describing “YTD-gross-compensation” attribute and filtered on condition “pay-type=Annually”|
| LC-REQ-F1     | -  |`1D/RejectStats_0_4096_no_outliers_filter_7_1.npy`        |[Lending Club (online credit market) Statistics database on rejected loan applications](https://www.lendingclub.com/info/download-data.action): describing “Amount Requested” attribute and filtered on condition “Employment between 0 and 5”|                  
| LC-REQ-F2     | -  |`1D/RejectStats_0_4096_no_outliers_filter_7_2.npy`        | [Lending Club (online credit market) Statistics database on rejected loan applications](https://www.lendingclub.com/info/download-data.action): describing “Amount Requested” attribute and filtered on condition “Employment between 5 and 10 (5 not included)”|
| LC-REQ-ALL    | -  |`1D/RejectStats_0_4096_no_outliers.npy`       |[Lending Club (online credit market) Statistics database on rejected loan applications](https://www.lendingclub.com/info/download-data.action): describing “Amount Requested” attribute|                                               
| LC-DTIR-F1    | -  |`1D/RejectStats_4_4096_no_outliers_filter_7_1.npy`        |[Lending Club (online credit market) Statistics database on rejected loan applications](https://www.lendingclub.com/info/download-data.action): describing “Debt-To-Income Ratio” attribute and filtered on condition “Employment between 0 and 5”|
| LC-DTIR-F2    | - | `1D/RejectStats_4_4096_no_outliers_filter_7_2.npy`        | [Lending Club (online credit market) Statistics database on rejected loan applications](https://www.lendingclub.com/info/download-data.action): describing “Debt-To-Income Ratio” attribute and filtered on condition “Employment between 5 and 10 (5 not included)”|
| LC-DTIR-ALL   | - |`1D/RejectStats_4_4096_no_outliers.npy`       | [Lending Club (online credit market) Statistics database on rejected loan applications](https://www.lendingclub.com/info/download-data.action): describing “Debt-To-Income Ratio” attribute|   
        
<a name="dawadata">1</a>: Data used in paper *Li, Chao, et al. "A data-and workload-aware algorithm for range queries under differential privacy." Proceedings of the VLDB Endowment 7.5 (2014): 341-352.*
                           
## Two-dimensional data
|      Name          |  Additional aliases |         Data File                  |      Source |
|--------------------|---------------------|------------------------------------|-------------|
| SF-CABS-E          | - |`2D/cabspottingE_256_256.npy`    |[San Francisco taxi cabs mobility traces dataset](http://crawdad.org/epfl/mobility/20090224/): describing the location of the end point of each trace|
| SF-CABS-S          | - |`2D/cabspottingS_256_256.npy`    |[San Francisco taxi cabs mobility traces dataset](http://crawdad.org/epfl/mobility/20090224/): describing the location of the start point of each trace|
| GOWALLA            | - |`2D/checkin_256_256.npy` |[Checking-in datasets from Gowalla social networking website](http://snap.stanford.edu/data/loc-gowalla.html) : describing the checking-in locations of users|
| BEIJING-CABS-E     | BJ-CABS-E |`2D/BeijingTaxiE_256_256.npy`    |[GPS trajectories (by 8602 taxi cabs in Beijing during May 2009)](http://sensor.ee.tsinghua.edu.cn/datasets.html): describing the GPS location of the end point of each trajectory|
| BEIJING-CABS-S     | BJ-CABS-S |`2D/BeijingTaxiS_256_256.npy`    |[GPS trajectories (by 8602 taxi cabs in Beijing during May 2009)](http://sensor.ee.tsinghua.edu.cn/datasets.html): describing the GPS location of the start point of each trajectory|
| ADULT-2D           | -|`2D/Adult_2D_256_256.npy`    |[Adult Census Dataset](https://archive.ics.uci.edu/ml/datasets/Adult): describing the “capital-gain” and “capital-loss” attributes of each person|
| MDSALARY-OVERT     | MD-SAL-2D| `2D/MDSalary2D_256_256.npy`  |[Maryland salary database (2012 state employee)](http://data.baltimoresun.com/salaries/state/cy2012/): describing “Annual Salary” and “Overtime earnings” attributes|
| LOAN-FUNDED-INCOME |LC-2D| `2D/Loan_2D_256_256.npy` |[Lending Club (online credit market) Statistics database on rejected loan applications](https://www.lendingclub.com/info/download-data.action): describing “Funded Amount” and “Annual Income” attributes|
| STROKE             | -|`2D/Stroke_2D_256_256.npy`   |[International Stroke Trial Database](http://www.trialsjournal.com/content/12/1/101/): describing “Age” and “Systolic blood pressure” attributes|
| TWITTER            | -|`2D/twitter_256_256.npy` | [Twitter Location Datatset](https://www.cs.duke.edu/courses/fall15/compsci590.4/assignment2/tweetstream.zip): describing tweet location in western USA|



