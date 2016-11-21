# Experiment Execution

The scripts in this directory can be used to run experiments and 
generate experimental output. Before proceeding, please be sure
to setup your environment and follow the initialization instructions
in the top-level README.

## sigmod2016.py

Detaild invocation instructions are available by running 
`sigmod2016.py --help`. The following invocations can be used
to generate a subset of the data that populates the plots in
the paper ``Principled Evaluation of Differentially Private Algorithms
using DPBench''.

### Figure 1.ab: Overall Error

```bash
python sigmod2016.py run --a1 "AHP*","HB","Identity","MWEM*","DAWA","PHP","MWEM","EFPA","DPCube","SF","Uniform" \
    --a2 "ALL" \
    --x1 'HEPTH','ADULTFRANK','INCOME','MEDCOST','NETTRACE','PATENT','SEARCHLOGS','BIDS-FJ','BIDS-FM','BIDS-ALL','MDSALARY','MDSALARY-FA','LC-REQ-F1','LC-REQ-F2','LC-REQ-ALL','LC-DTIR-F1','LC-DTIR-F2','LC-DTIR-ALL' \
    --x2 'SF-CABS-E','SF-CABS-S','GOWALLA','BEIJING-CABS-E','BEIJING-CABS-S','ADULT-2D','MDSALARY-OVERT','LOAN-FUNDED-INCOME','STROKE' \
    --d1 4096 --d2 "(128,128)" \
    --s1 1000,100000,10000000 --s2 10000,1000000,100000000 \
    --se 4 --out "fig_main.json"    
```
    

### Figure 2.ab: Error by Shape

```bash
    python sigmod2016.py run --a1 "EFPA","HB","Identity","MWEM*","DAWA","PHP","MWEM","Uniform" \
    --a2 "Uniform","AGrid","DAWA","HB","Identity" \
    --x1 'HEPTH','ADULTFRANK','INCOME','MEDCOST','NETTRACE','PATENT','SEARCHLOGS','BIDS-FJ','BIDS-FM','BIDS-ALL','MDSALARY','MDSALARY-FA','LC-REQ-F1','LC-REQ-F2','LC-REQ-ALL','LC-DTIR-F1','LC-DTIR-F2','LC-DTIR-ALL' \
    --x2 'SF-CABS-E','SF-CABS-S','GOWALLA','BEIJING-CABS-E','BEIJING-CABS-S','ADULT-2D','MDSALARY-OVERT','LOAN-FUNDED-INCOME','STROKE' \
    --d1 4096 --d2 "(128,128)" \
    --s1 1000 --s2 10000 \
    --se 4 --out "fig_shape.json"   
```
    
### Figure 2.c: Error by Size

```bash
    python sigmod2016.py run --a1 "Identity" \
    --a2 "Uniform","AGrid","DAWA","HB","Identity" \
    --x1 'HEPTH' \
    --x2 'BEIJING-CABS-E','ADULT-2D' \
    --d1 128 --d2 "(256,256)","(128,128)","(64,64)","(32,32)" \
    --s1 1000 --s2 10000,1000000 \
    --se 4 --out "fig_domain_size.json"
```
