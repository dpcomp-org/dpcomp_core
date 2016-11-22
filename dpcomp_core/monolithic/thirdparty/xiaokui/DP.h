#pragma once
#include "Utilities.h"
#include "HTree.h"
#include <float.h>

class DP
{
public:
	DP(void);
	DP(int _N, int _B);
	~DP(void);
	void run(vector<double>& hist);
	void outputNoisyCounts_NoiseFirst(Histogram& noisyHist, double epsilon, ofstream& o_file);
	void outputNoisyCounts_StructureFirst(vector<double>& counts, vector<double>& cutCounts, 
		double epsilon1, double epsilon2, double maxF, vector<double>& ovec, MTRand& temp_rand);
	int  findOptK(vector<double>& hist, double epsilon);
	static double getOptEps1(int n, int k, double epsilon, double maxF);
	vector<int> collParStra();

private:
	void initialPara(vector<double>& hist);
	double calSSE(int i, int j);
	vector<int> adjustBoundery(vector<double>& hist, double epsilon1, double maxF ,MTRand& temp_rand);
	void innerLoop(int startIndex, int i, int k);
    vector<double> boost(vector<double>& ori_hist, int begin, int end, double epsilon2,MTRand& temp_rand);
    void addNoise2Partition(vector<double>noisyHist, int begin, int end, double epsilon, ofstream& o_file);

private:
	int K;               ///merged bin number
	int N;               ///original bin number
	vector<double> P;    ///sum F[k]
	vector<double> PP;   ///sum F[k]^2
	vector<vector<double> > SSEStar;
	vector<vector<int> > solution;
};
