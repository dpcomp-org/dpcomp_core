// Implemented by Jia XU
// 2011-05
// Please contact use:
// xujia@ise.neu.edu.cn 

#include "Utilities.h"
#include "DP.h"
#include "M_DP.h"

//*************Function Declarations**************
//Laplacian Mechanism (Dwork)
void dwork (vector<double>& counts, double epsilon, ofstream& o_file);

//Mean-NoiseFirst
void noiseFirst (vector<double>& counts, double epsilon, ofstream& o_file);

//Mean-StructureFirst
void structureFirst(vector<double>& counts, double epsilon, ofstream& o_file);

//Median-NoiseFirst
void m_noiseFirst(vector<double>& counts, double epsilon, ofstream& o_file);

//Median-StructureFirst
void m_structureFirst(vector<double>& counts, double epsilon, ofstream& o_file);


int main(int argc, char *argv[]){
	string method = "m_NoiseFirst";//can be "Dwork", "NoiseFirst","StructureFirst","m_NoiseFirst" or "m_StructureFirst"
	double epsilon = 1;              
	string histogram_file = "dataset.txt";   
	string result_file;

	string dataSetName = histogram_file;
	size_t loc = dataSetName.find(".");
	dataSetName.erase(loc, 4);

	result_file = "rlt-";
	result_file += method;
	result_file += "-";
	result_file += dataSetName;
	result_file += ".txt";

	cout<<"****************************************************\n";
	cout<<dataSetName;
	cout<<"  "<<method;
	cout<<"  "<<epsilon;
	cout<<"  "<<result_file<<endl;
	cout<<"****************************************************\n\n";


	Histogram histogram;
	Utilities::readFile(histogram_file, histogram.counts);
	ofstream o_file;
	o_file.open(result_file.c_str(),ios::app);

	if(method.compare("Dwork") == 0){
		dwork(histogram.counts, epsilon, o_file);
	}else if(method.compare("NoiseFirst") == 0){
		noiseFirst(histogram.counts, epsilon, o_file);
	}else if (method.compare("StructureFirst") == 0){
		structureFirst(histogram.counts, epsilon, o_file);
	}else if (method.compare("m_NoiseFirst") == 0){
		m_noiseFirst(histogram.counts, epsilon, o_file);
	}else if (method.compare("m_StructureFirst") == 0){
		m_structureFirst(histogram.counts, epsilon, o_file);
	}else{
		cout<<"Error: undefined method name.\n";
		getchar();
		exit(0);
	}

	o_file.close();

    return 0;
}


void dwork(vector<double>& counts, double epsilon, ofstream& o_file){
	for(vector<int>::size_type i = 0; i < counts.size(); i ++)
		o_file<<counts[i] + Utilities::getLapNoise((1.0)/epsilon)<<" ";
	o_file<<endl;
}


void noiseFirst(vector<double>& counts, double epsilon, ofstream& o_file){
	int bin_num = (int)(counts.size());
	Histogram noisyHist;
	for(vector<int>::size_type i = 0; i < counts.size(); i ++)
		noisyHist.counts.push_back(counts[i] + Utilities::getLapNoise((1.0)/epsilon));
	int optK;
	{
		DP dp(bin_num, bin_num);
		optK = dp.findOptK(noisyHist.counts, epsilon);
		cout<<optK<<endl;
	}

	DP dp(bin_num, optK);
	dp.outputNoisyCounts_NoiseFirst(noisyHist, epsilon, o_file);
}


void structureFirst(vector<double>& counts, double epsilon, ofstream& o_file){
	///obtain the total counts in the original histogram
	int bin_num = (int)(counts.size());
	int merge_bin_num = ceil(bin_num * K_RATIO); 
	double total_counts = 0;
	for(vector<int>::size_type i = 0; i < counts.size(); i ++)
		total_counts += counts[i];
	double max_freq = (total_counts / bin_num) * 10000;
	vector<double> counts_smooth_max_freq;
	for(int i = 0; i < bin_num; i ++){
		if(counts[i] > max_freq)
			counts_smooth_max_freq.push_back(max_freq);
		else
			counts_smooth_max_freq.push_back(counts[i]);
	}

	double epsilon1;
	epsilon1 = DP::getOptEps1(bin_num, merge_bin_num, epsilon, max_freq);
	double epsilon2 = epsilon - epsilon1;
	DP dp(bin_num, merge_bin_num);
	dp.outputNoisyCounts_StructureFirst(counts, counts_smooth_max_freq, epsilon1, epsilon2, max_freq, o_file);
}


void m_noiseFirst(vector<double>& counts, double epsilon, ofstream& o_file){
	int bin_num = (int)(counts.size());
	Histogram noisyHist;
	for(vector<int>::size_type i = 0; i < counts.size(); i ++)
		noisyHist.counts.push_back(counts[i]+ Utilities::getLapNoise((1.0)/epsilon));

	int optK;
	M_DP m_dp(bin_num, bin_num);
	optK = m_dp.findOptK(noisyHist.counts, epsilon);
	m_dp.setK(optK);
	m_dp.outputNoisyCounts_M_NoisyFirst(noisyHist, epsilon, o_file);

}


void m_structureFirst(vector<double>& counts, double epsilon, ofstream& o_file){
	int bin_num = (int)(counts.size());
	int merge_bin_num = ceil(bin_num * K_RATIO); 
	double total_counts = 0;
	for(vector<int>::size_type i = 0; i < counts.size(); i ++)
		total_counts += counts[i];
	double max_freq = (total_counts / bin_num) * 10000;
	double epsilon1 = M_DP::getOptEps1(bin_num, merge_bin_num, epsilon, max_freq);
	double epsilon2 = epsilon - epsilon1;
	M_DP m_dp(bin_num, merge_bin_num);
	m_dp.outputNoisyCounts_M_StructureFirst(counts, epsilon1, epsilon2, o_file);
}


