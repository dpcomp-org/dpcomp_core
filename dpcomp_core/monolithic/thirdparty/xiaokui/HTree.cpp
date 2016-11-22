#include "HTree.h"

HTree::HTree(void){
}


HTree::~HTree(void){
	tree.clear();
}


HTree::HTree(int fan_out, vector<double>& hist_seg, int para_begin, int para_end, double epsilon,MTRand& temp_rand){
	Utilities util;
	this->fan_out = fan_out;
	ori_bin_num = para_end - para_begin;
	this->height = int(ceil(log(double (ori_bin_num))/log(double (fan_out)))) + 1;

	this->epsilon = epsilon;
	double lamda = this->height/epsilon;

	///construct the hay tree
	tree.resize(this->height + 1);
	for(int i = para_begin; i < para_end; i ++){
		double noise;
		noise = hist_seg[i] + util.getLapNoise(lamda,temp_rand);
		HNode newNode(i, i, hist_seg[i], noise);
		tree[1].push_back(newNode);
	}
	int start = ori_bin_num;
	for(int i = 0; i < int(pow(double(fan_out), this->height - 1))-ori_bin_num; i ++){
		HNode newNode(start + i, start + i, 0, 0);
		tree[1].push_back(newNode);
	}
	int underLayer = 1;
	for(vector<int>::size_type i = 2; i < tree.size(); i ++){
		for(int j = 0; j < int(tree[underLayer].size())/fan_out; j ++){
			int base = j * fan_out;
			int begin = tree[underLayer][base].start;
			int end = tree[underLayer][base + fan_out - 1].end;
			double sum = 0;
			for(int x = base; x < base + fan_out; x ++){
				sum += tree[underLayer][x].count;
			}
			double noise = sum;
			if(begin < ori_bin_num)
				noise += util.getLapNoise(lamda,temp_rand);
			HNode newNode(begin, end, sum, noise);
			tree[i].push_back(newNode);
		}
		underLayer ++;
	}
}


vector<double> HTree::returnLeaves(){
	vector<double> leaves;
	for(int i = 0; i < ori_bin_num; i ++){
		leaves.push_back(tree[1][i].hbar);
	}
	return leaves;
}

void HTree::inference(){
	///go bottom up to compute z[v]
	for(vector<int>::size_type i = 0; i < tree[1].size(); i ++){
		tree[1][i].zv = tree[1][i].noise;
	}
	int underLayer = 1;
	for(vector<int>::size_type i = 2; i < tree.size(); i ++){		
		double alpha = pow(double(fan_out), int(i) - 1); ///i = recent height
		for(int j = 0; j < int(tree[underLayer].size())/fan_out; j ++){
			int base = j * fan_out;
			int begin = tree[underLayer][base].start;
			int end = tree[underLayer][base + fan_out - 1].end;
			double zvSum = 0;
			for(int x = base; x < base + fan_out; x ++){
				zvSum += tree[underLayer][x].zv;
			}
			tree[i][j].total_z_children = zvSum;
			double a = ((fan_out - 1) * alpha) * tree[i][j].noise;
			double b = (alpha - 1) * zvSum;
			tree[i][j].zv = (a + b)/(fan_out * alpha - 1);
		}
		underLayer ++;
	}

	///go top down to compute hbar[v]
    int upLayer = height;
    tree[height][0].hbar = tree[height][0].zv;///root
	for(vector<int>::size_type i = height - 1; i > 0; i --){
		for(vector<int>::size_type j = 0; j < tree[upLayer].size(); j ++){
			int parent = j;
			double addup = (tree[upLayer][parent].hbar - tree[upLayer][parent].total_z_children)/fan_out;
			int base = j * fan_out;
			for(int x = base; x < base + fan_out; x ++){
				tree[i][x].hbar = tree[i][x].zv + addup;
			}
		}
		upLayer --;
	}
}
