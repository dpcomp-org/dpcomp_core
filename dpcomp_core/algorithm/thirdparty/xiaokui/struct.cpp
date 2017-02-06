// The mean-structureFirst algorithm extracted from main.cpp

#include "struct.h"


//Mean-StructureFirst
void structureFirst(double* oricounts, int n, double* noicounts, int n1, double epsilon,long seed){
	///obtain the total counts in the original histogram
	int bin_num = n;
	int merge_bin_num = ceil(bin_num * K_RATIO); 
	double total_counts = 0;
    vector<double> counts(oricounts, oricounts+n), ovec;
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

	// set up random state
	MTRand temp_rand(seed);

	double epsilon1;
	epsilon1 = DP::getOptEps1(bin_num, merge_bin_num, epsilon, max_freq);
	double epsilon2 = epsilon - epsilon1;
	DP dp(bin_num, merge_bin_num);
    ovec.resize(n);
	dp.outputNoisyCounts_StructureFirst(counts, counts_smooth_max_freq, epsilon1, epsilon2, max_freq, ovec, temp_rand);
    std::copy(ovec.begin(), ovec.end(), noicounts);
}

