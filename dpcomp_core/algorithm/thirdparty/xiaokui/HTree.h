// HTree.h
// Implemented by Jia XU
// 2011-05
// A C++ implementation of Hay et. al.'s method, which is named as Boost in the paper.

// Reference
// Boosting the Accuracy of Differentially-Private Queries Through Consistency.
// Michael Hay, Vibhor Rastogi, Gerome Miklau, Dan Suciu, VLDB 2010 



#pragma once

#include <vector>
#include "Utilities.h"
using namespace std;

struct HNode
{
	HNode(void);
	HNode(int _start, int _end, double _count, double _noise){
		start = _start;
		end   = _end;
		count = _count;
		noise = _noise;
	}
	int start;
	int end;
	double count;
	double noise;
	double zv;
	double hbar;
	double total_z_children;
};

class HTree
{
public:
	HTree(void);
	~HTree(void);
	HTree(int fan_out, vector<double>& hist_seg, int begin, int end, double epsilon,MTRand& temp_rand);
	vector<double> returnLeaves();
	void inference();
	
private:
	int fan_out;
	int height;
	int ori_bin_num;
	vector<vector<HNode> > tree;
	double epsilon;

};
