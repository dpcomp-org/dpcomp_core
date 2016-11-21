# Plots 

## Install latest R

On Ubuntu 14.04 use the following steps to install the latest version of R.

```bash
sudo sh -c 'echo "deb http://cran.rstudio.com/bin/linux/ubuntu trusty/" >> /etc/apt/sources.list'
gpg --keyserver keyserver.ubuntu.com --recv-key E084DAB9
gpg -a --export E084DAB9 | sudo apt-key add -
sudo apt-get update
sudo apt-get -y install r-base
```

Please also make sure to add the following R libraries:

```
install.packages('ggplot2',dependencies = TRUE)
install.packages('jsonlite')
install.packages('optparse')
install.packages('data.table')
```

To reproduce figures in the paper, run the R code 

```bash
Rscript plot.R -f fig_main.json -t main -d 1
Rscript plot.R -f fig_main.json -t main -d 2
Rscript plot.R -f fig_shape.json -t shape -d 1
Rscript plot.R -f fig_shape.json -t shape -d 2
Rscript plot.R -f fig_domain_size.json -t domain_size
```

```
Usage: plot.R [options]
Options:
	-f FILE, --file=FILE
		dataset file name
	-o OUT, --out=OUT
		output file name [default = out.pdf]
	-d DIMENSION, --dimension=DIMENSION
		output file name [default = 1]
	-t TYPE, --type=TYPE
		plot type: main/shape/domain_size [default = main]
	-h, --help
		Show this help message and exit
```
