#!/usr/bin/env Rscript

library(jsonlite)
library(optparse)
library(ggplot2)
library(data.table)
library(digest)

#parse command line arguments
option_list = list(
  make_option(c("-f", "--file"), type="character", default=NULL, 
              help="dataset file name"),
  make_option(c("-o", "--out"), type="character", default="out.pdf", 
              help="output file name [default = %default]"),
  make_option(c("-d", "--dimension"), type="integer", default=1, 
              help="output file name [default = %default]"),
  make_option(c("-t", "--type"), type="character", default="main", 
              help="plot type: main/shape/domain_size [default = %default]"),
  make_option(c("-q", "--quick"), action="store_true", dest="quick", default =FALSE,
  			  help="plot the quick version")

); 
 

apply_dic <- function(dic,list){
	result = list()
	for (item in list){
  		result = c(result,dic[item])
	}
	return(result)
}

raw_colors = c('#1B9E77','#D95F02','#7570B3','#E7298A','#66A61E','#E6AB02','#A6761D','#666666','#FFFFFF')


plot_domain_size <- function(df,raw_colors,out_file){
	df = df[df$d_dimensionality ==2,]	
	hue_order = c('Uniform','AGrid','DAWA','HB','Identity')
	x_order = c("32,32","64,64","128,128","256,256")
	LSDict = c('Uniform'='solid','AGrid'='solid','DAWA'='solid','HB'='dashed','Identity'='dotted')
	MSDict = c('Uniform'=19,'AGrid'=19,'DAWA'=19,'HB'=17,'Identity'=NaN)          
	CrDict = c('Uniform'=raw_colors[8],'AGrid'=raw_colors[1],'DAWA'=raw_colors[2],'HB'=raw_colors[8],'Identity'=raw_colors[8])


	df$d_scale = factor(df$d_scale)
	df$d_nickname = factor(df$d_nickname)
	df$a_name = factor(df$a_name, levels = hue_order)
	df$d_domain = factor(df$d_domain_size,levels=c(32,64,128,256))
	p = ggplot(data=df, aes(x=d_domain, y=log10(mean_error), color=a_name, linetype=a_name, shape=a_name)) 
	p = p + geom_point(size=3,stat="summary",fun.y = "mean")
	p = p + geom_line(aes(group=a_name),stat="summary",fun.y = "mean", size=1)
	p = p + facet_grid(d_nickname ~ d_scale)	

	p = p + scale_colour_manual(values = CrDict, name="Algorithm\n")
	p = p + scale_shape_manual(values = MSDict, name="Algorithm\n")
	p = p + scale_linetype_manual(values = LSDict, name="Algorithm\n")#	

	p = p + scale_x_discrete(labels = x_order,drop=FALSE)#	

	p = p + scale_y_continuous(breaks=seq(-10, 10, 1),limits=c(-6,-2))
	p = p + xlab('\nDOMAIN SIZE') + ylab('Scaled Per Query L2 Error (Log10)\n')
	p = p + theme(axis.text.x = element_text(angle = 90, vjust = 0.5, hjust=0, size=14, face='plain'))
	p = p + theme(axis.text.y = element_text(size=14, face='plain'))
	p = p + theme(axis.title.y = element_text(size=16, face='plain'))
	p = p + theme(axis.title.x = element_text(size=16, face='plain'))
	p = p + theme(legend.text = element_text(size=14, face='plain'))
	p = p + theme(legend.title = element_text(size=16, face='bold'))
	p = p + theme(strip.text = element_text(size=14, face='bold'))
	p = p + theme(legend.background = element_rect(fill="white", size=.5, linetype="dotted"))	

	ggsave(filename=out_file, plot = p, width = 7, height = 7)
}


plot_shape <- function(df,dimension,raw_colors, out_file){
	df = df[df$d_dimensionality == dimension,]	
	#df=data.table(df)
	#df[,mean_error:= mean(mean_error),by=list(d_nickname,a_name)]
	ylimt = if(dimension == 1) c(-4,-2) else c(-4,-2)
	x_order_1D = c('BIDS-FJ','BIDS-ALL','BIDS-FM','PATENT','HEPTH','LC-DTIR-F1','LC-DTIR-ALL','LC-DTIR-F2',
	         'SEARCH','LC-REQ-F2','LC-REQ-ALL','LC-REQ-F1','MEDCOST','ADULT','INCOME','MD-SAL-FA',
	         'MD-SAL','NETTRACE')
	x_order_2D = c('GOWALLA','STROKE','LC-2D','MD-SAL-2D','ADULT-2D','SF-CABS-S','SF-CABS-E','BJ-CABS-S','BJ-CABS-E')	
	hue_order_1D = c('Identity','DAWA','Uniform','EFPA','PHP','HB','MWEM','MWEM*')
	hue_order_2D = c('Uniform','AGrid','DAWA','HB','Identity')
	LSDict_1D = c('Identity'='dotted','DAWA'='solid','Uniform'='solid','EFPA'='solid',
	          'PHP'='solid','HB'='solid','MWEM'='solid','MWEM*'='solid')
	LSDict_2D = c('Uniform'='solid','AGrid'='solid','DAWA'='solid','HB'='dashed','Identity'='dotted')	
	MSDict_1D= c('Identity'=NaN,'DAWA'=19,'Uniform'=19,'EFPA'=19,
	          'PHP'=19,'HB'=17,'MWEM'=1,'MWEM*'=17)
	MSDict_2D = c('Uniform'=19,'AGrid'=19,'DAWA'=19,'HB'=17,'Identity'=NaN)            
	CrDict_1D = c('Identity'=raw_colors[8],'DAWA'=raw_colors[3],'Uniform'=raw_colors[8],'EFPA'=raw_colors[1],
	          'PHP'=raw_colors[4],'HB'=raw_colors[8],'MWEM'=raw_colors[6],'MWEM*'=raw_colors[6])
	CrDict_2D = c('Uniform'=raw_colors[8],'AGrid'=raw_colors[1],'DAWA'=raw_colors[2],'HB'=raw_colors[8],'Identity'=raw_colors[8])

	x_order   = if(dimension == 1) x_order_1D else x_order_2D
	hue_order = if(dimension == 1) hue_order_1D else hue_order_2D
	LSDict    = if(dimension == 1) LSDict_1D  else LSDict_2D
	MSDict    = if(dimension == 1) MSDict_1D  else MSDict_2D
	CrDict    = if(dimension == 1) CrDict_1D  else CrDict_2D
	

	df$d_nickname = factor(df$d_nickname, levels=x_order)
	df$a_name = factor(df$a_name, levels = hue_order)	

	p = ggplot(data=df, aes(x=d_nickname, y=log10(mean_error), color=a_name, linetype=a_name, shape=a_name)) 
	p = p + geom_point(size=3,stat="summary",fun.y = "mean")
	p = p + geom_line(aes(group=a_name),stat="summary",fun.y = "mean", size=1)	

	LegendName = paste(as.character(dimension),"D Algorithm\n",sep="")
	p = p + scale_colour_manual(values = CrDict, name=LegendName)
	p = p + scale_shape_manual(values = MSDict, name=LegendName)
	p = p + scale_linetype_manual(values = LSDict, name=LegendName)	
	p = p + scale_x_discrete(labels = x_order,drop=FALSE)	
	p = p + theme(axis.text.x = element_text(angle = 90, vjust = 0.5, hjust=0, size=14, face='plain'))
	p = p + scale_y_continuous(breaks=seq(-10, 10, 1),limits=ylimt)
	p = p + xlab('\nDATASET') + ylab('Scaled Per Query L2 Error (Log10)\n')
	p = p + theme(axis.text.y = element_text(size=14, face='plain'))
	p = p + theme(axis.title.y = element_text(size=16, face='plain'))
	p = p + theme(axis.title.x = element_text(size=16, face='plain'))
	p = p + theme(legend.text = element_text(size=14, face='plain'))
	p = p + theme(legend.title = element_text(size=16, face='bold'))
	p = p + theme(strip.text = element_text(size=14, face='bold'))
	p = p + theme(legend.background = element_rect(fill="white", size=.5, linetype="dotted"))

	ggsave(filename=out_file, plot = p, width = 7, height = 7)
}
plot_main <- function(df,dimension,out_file,quick){
	df = df[df$d_dimensionality == dimension,]	


	mofm = data.table(df)
 	mofm[,mean_error:=mean(mean_error),by=list(d_domain_size, a_name,d_scale)]
 	algo_labels = c('Identity'="IDENTITY", "DPCube"="DPCUBE","Uniform"="UNIFORM","UGrid"="UGRID","AGrid"="AGRID","QuadTree"="QUADTREE")
	x_order_1D = c('Identity','HB','MWEM*','DAWA','PHP','MWEM','EFPA','DPCube','AHP*','SF','Uniform')
	x_order_2D = c('Identity','HB','AGrid','MWEM','MWEM*','DAWA','QuadTree','UGrid','DPCube','AHP','Uniform')
	x_order   = if(dimension == 1) x_order_1D else x_order_2D
	ylimt = if(dimension == 1) c(-7,-2) else c(-8,-2)
	scale_level = if (dimension ==1 ) c('1000','100000','10000000') else c('10000','1000000','100000000')

	df$d_scale = factor(df$d_scale,levels=scale_level)
	hlineHB = df[df$a_name=="HB",]
	hlineID = df[df$a_name=='Identity',]

	df$d_fname = factor(df$d_nickname)
	df$a_name = factor(df$a_name,levels=x_order)
	mofm$a_name = factor(mofm$a_name,levels=x_order)

	p = ggplot(data=df, aes(x=a_name, y=log10(mean_error))) 
	p = p + scale_x_discrete(labels=algo_labels,drop=FALSE)

	# hline to highlight data independent methods
	p = p + geom_hline(data = hlineID, aes(yintercept = log10(mean_error)),linetype="dotted",alpha=1,size=.7)
	p = p + geom_hline(data = hlineHB, aes(yintercept = log10(mean_error)),linetype="solid")	

	# black dots for each dataset
	p = p + geom_point(size=2.5)
	# white diamonds for mean over datasets	
	if (quick == FALSE)
	{
		p = p + geom_point(size=3.5, data=mofm,aes(x=a_name, y=log10(mean_error)), color='black', shape=23, fill='white')	
	}
	p = p + facet_grid(. ~ d_scale,drop =FALSE)	

	p = p + scale_y_continuous(breaks=seq(-10, 10, 1),limits = ylimt)
	p = p + theme(axis.text.x = element_text(angle = 90, vjust = 0.5, hjust=0, size=12, face='bold'))
	p = p + theme(axis.title.y = element_text(size=16, face='plain'))
	p = p + theme(axis.title.x = element_text(size=14, face='plain'))
	p = p + xlab('\nALGORITHM') + ylab('Scaled L2 Error Per Query (Log10)\n')

	ggsave(filename=out_file, plot = p, width = 7, height = 7)

}

#parse command
opt_parser = OptionParser(option_list=option_list);
opt = parse_args(opt_parser);
if (is.null(opt$file)){
  print_help(opt_parser)
  stop("An input file must be supplied.", call.=FALSE)
}
input_list = unlist(strsplit(toString(opt['file']),','))
out_file = toString(opt['out'])
dimension = opt['dimension']
type = opt['type']
QUICK = opt['quick']
#load input from list of files
df = data.frame()
for (file in input_list){
	df_single= fromJSON(file)
	df <- rbind(df,df_single)
}
#deal with inconsistent data names
df$d_nickname = gsub("\\<MDSALARY$","MD-SAL",df$d_nickname)
df$d_nickname = gsub("\\<MDSALARY-FA$","MD-SAL-FA",df$d_nickname)
df$d_nickname = gsub("\\<MDSALARY-OVERT$","MD-SAL-2D",df$d_nickname)
df$d_nickname = gsub("\\<SEARCHLOGS$","SEARCH",df$d_nickname)
df$d_nickname = gsub("\\<ADULTFRANK$","ADULT",df$d_nickname)
df$d_nickname = gsub("\\<LOAN-FUNDED-INCOME$","LC-2D",df$d_nickname)
df$d_nickname = gsub("\\<BEIJING-CABS-E$","BJ-CABS-E",df$d_nickname)
df$d_nickname = gsub("\\<BEIJING-CABS-S$","BJ-CABS-S",df$d_nickname)

if (type =="main") { 
	plot_main(df,dimension,out_file,QUICK)
	}else if (type =="shape") {
		plot_shape(df,dimension,raw_colors,out_file)
		}else if (type=="domain_size"){
			plot_domain_size(df,raw_colors,out_file)
		}else {
			print("Wrong type of figure.See --help")
		}


