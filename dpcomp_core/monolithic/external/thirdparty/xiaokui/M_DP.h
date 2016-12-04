#pragma once
#include <float.h>
#include "Utilities.h"
#include "HTree.h"

class M_DP
{
public:
	M_DP(int _N, int _B);
	M_DP();
	~M_DP(void);
	void setK(int _k);
	void run(vector<double>& hist);
	vector<int> collParStra();
	void outputNoisyCounts_M_NoisyFirst(Histogram& noisyHist, double epsilon, ofstream& o_file);
	void addNoise2Partition(vector<double>noisyHist, int begin, int end, double epsilon, ofstream& o_file);
	void outputNoisyCounts_M_StructureFirst(vector<double>& counts, 
	double epsilon1, double epsilon2, ofstream& o_file,MTRand& temp_rand);
    int findOptK(vector<double>& hist, double epsilon);
	static double getOptEps1(int n, int k, double epsilon, double maxF);

private:
	void sort(vector<double>& D, int start, int end);
	double calSAE(int i, int j, vector<double>& hist);
	void innerLoop(int startIndex, int i, int k, vector<double>& hist);
	vector<double> boost(vector<double>& ori_hist, int begin, int end, double epsilon2,MTRand& temp_rand);
	vector<int> adjustBoundary(vector<double>& hist, double epsilon1,MTRand& temp_rand);
	inline void Swap(vector<double>& hist, int i, int j);
	//int Partition(vector<double>& hist,int first,int last);
	void Partition(vector<double>& hist,int first,int last, int &pivotindex, int &pivotcount);
	int FindKth(vector<double>& hist, int left, int right, int k);
public:
	double getMedian(int start, int end, vector<double>& hist);

private:
	int K;               ///merged bin number
	int N;               ///original bin number
	vector<vector<double> > SAEStar;
	vector<vector<int> >    solution;
	vector<vector<double> >    medianMatrix;

	//vector<vector<double>> medianMatrix;
};
