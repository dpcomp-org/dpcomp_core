#include "M_DP.h"

//M_DP::M_DP(void){
//	vector<int> int_array(N, INT_MAX);
//	medianMatrix.resize(N, int_array);
//}

void M_DP::setK(int _k){
	K = _k;
}

M_DP::M_DP(int _N, int _B){
	N = _N;
	K = _B;
	vector<double> doubleT_B(_B, FLT_MAX);
	vector<int> intT(_B, INT_MAX);
	SAEStar.resize(_N, doubleT_B);
	solution.resize(_N, intT);
	vector<double> doubleT_N(N, FLT_MAX);
	medianMatrix.resize(N, doubleT_N);

}

M_DP::M_DP(){

}


M_DP::~M_DP(void){
}



inline void M_DP::Swap(vector<double>& hist, int i, int j)
{
	double tmp = hist[i];
	hist[i] = hist[j];
	hist[j] = tmp;
}



void M_DP::Partition(vector<double>& hist,int first,int last, int &pivotindex, int &pivotcount)
{
	int k,p = first;
	int chooseIndex = int(floor((first+last) / 2.0));
	Swap(hist, first, chooseIndex);
	double piv;
	piv = hist[first];
	pivotcount = 0;
	for(k=first+1;k<=last;k++)
	{
		if (hist[k] < piv)
		{
			p++;            
			Swap(hist,k,p);
		}
		else if(fabs(hist[k]- piv) < 1e-6)
		{
			pivotcount ++;
		}
	}
	Swap(hist,p,first);
	pivotindex = p;
}


int M_DP::FindKth(vector<double>& hist, int left, int right, int k)
{
	//int flag = false;
	//return the k-th element in a
	int pivotIndex = 0, pivotCount = 0;
	Partition(hist,left,right, pivotIndex, pivotCount);
	//cout<<"Pivot: "<<hist[pivotIndex]<<endl;
	if (pivotIndex<= k && k<= pivotCount+ pivotIndex)      {return k;}
	else if (k < pivotIndex)  return FindKth(hist, left, pivotIndex-1, k);
	else                      return FindKth(hist,pivotIndex+1, right, k);
}

double M_DP::getMedian(int start, int end, vector<double>& wholeHist)
{   //return median
	//if(start == end)
	//	return wholeHist[start];

	vector<double> histSeg;
	for(int k = start; k <= end; k ++){
		histSeg.push_back(wholeHist[k]);
	}
	int length = end - start + 1;
	//cout<<start<<"\t"<<end<<endl;
	int kIndex = FindKth(histSeg, 0, length-1, int(floor((length+1)/2.0))-1);
	if((length % 2) != 0){
		//如果是奇数
		return histSeg[kIndex];
	}else{
		///如果是偶数
		double minV = FLT_MAX;
		for(int i = kIndex+1; i < int(histSeg.size()); i ++){
			if(histSeg[i] < minV){
				minV = histSeg[i];
			}
		}
		return (histSeg[kIndex]+minV)/2.0;
	}
}


///use initialPara before calSAE
double M_DP::calSAE(int i, int j, vector<double>& hist){
	if(i == j)
		return 0.0;
	double median;
	if(medianMatrix[i][j] < FLT_MAX - 1){
		median = medianMatrix[i][j];
	}
	else{
       median = getMedian(i, j, hist);
	   medianMatrix[i][j] = median;
	}
	double SAE = 0.0;
	for(int start = i; start <= j; start ++)
		SAE += fabs(hist[start] - median);


    return SAE;

}


void M_DP::run(vector<double>& hist){

	for(int i = 0; i < K; i ++){
		SAEStar[i][i] = 0;
		solution[i][i] = i;
	}

	for(int i = 1; i < N; i ++){
		SAEStar[i][0] = calSAE(0, i, hist);	
		solution[i][0]= 0;
	}

	for(int k = 1; k < K; k ++){
		for(int i = k + 1; i < N; i ++){
			innerLoop(k - 1, i, k, hist);
		}
	}
}

void M_DP::innerLoop(int startIndex, int i, int k, vector<double>& hist){
	double minDist = FLT_MAX;
	for(int j = startIndex; j < i; j ++){
		double tempSAE = SAEStar[j][k-1] + calSAE(j+1, i, hist);///+noise;
		if(tempSAE < minDist){
			solution[i][k] = j + 1;
			SAEStar[i][k] = tempSAE;
			minDist = tempSAE;
		}
	}
}


void M_DP::outputNoisyCounts_M_NoisyFirst(Histogram& noisyHist, double epsilon, ofstream& o_file){
	run(noisyHist.counts);
	noisyHist.partition = collParStra();
	for(vector<int>::size_type i = 0; i < noisyHist.partition.size() - 1; i ++){
		addNoise2Partition(noisyHist.counts, noisyHist.partition[i], noisyHist.partition[i+1], epsilon, o_file);
	}
	o_file<<endl;
}

void M_DP::addNoise2Partition(vector<double>noisyHist, int begin, int end, double epsilon, ofstream& o_file){
	if(end == begin + 1){
		o_file<<noisyHist[begin]<<" ";
		return;
	}
	int D_size = end - begin;
	double median_value = medianMatrix[begin][end-1];

	double HbarDbar_merge = 0;
	for(int i = begin; i < end; i ++){
		HbarDbar_merge += fabs(median_value - noisyHist[i]);
	}

	if(HbarDbar_merge >= (4*(D_size-1)+1)/(epsilon)){
		for(int i = begin; i < end; i ++)
			o_file<<noisyHist[i]<<" ";
	}else{
		for(int i = begin; i < end; i ++)
			o_file<<median_value<<" ";
	}
}

int M_DP::findOptK(vector<double>& hist, double epsilon){
    int optK;
	for(int i = 0; i < K; i ++){
		SAEStar[i][i] = 0;
		solution[i][i] = i;
	}

	for(int i = 1; i < N; i ++){
		SAEStar[i][0] = calSAE(0, i, hist);	
		solution[i][0]= 0;
	}

	for(int k = 1; k < K; k ++){
		for(int i = k + 1; i < N; i ++){
			innerLoop(k - 1, i, k, hist);
		}
	}

	double minValue = FLT_MAX;

	for(int i = 0; i < K; i ++){
		double estimatedErr = SAEStar[N-1][i] - (3*(N-i))/epsilon;
		if(estimatedErr < minValue){
			minValue = estimatedErr;
			optK = i+1;
		}
	}
	return optK;
}


vector<int> M_DP:: collParStra(){
	vector<int> boundary;
	boundary.resize(K + 1);
	boundary[K] = N;
	boundary[0] = 0;

	int n = N - 1;
	for(int i = K - 1; i > 0; i --){
		int j = solution[n][i];
		if((j == INT_MAX) && (n == i)){
			for(int x = 1; x <= n; x++)
				boundary[x] = x;
			break;
		}		
		boundary[i] = j;
		n = j - 1;
	}

	///for testing 
	//for(int i = 0; i < int(boundary.size()); i ++){
	//	cout<<boundary[i]<<" ";
	//}
	//cout<<endl;

	return boundary;
}


void M_DP::sort(vector<double>& D, int start, int end){
	///	sort(a,0,9);
	int z,y;
	double k;

	if(start<end){
		z=start;
		y=end;
		k=D[z]; 
		do{
			while((z<y)&&(D[y]>=k))
				y--;
			if(z<y)          //右边的元素小于k，移到k左
			{
				D[z]=D[y];
				z=z+1;
			}
			while((z<y)&&(D[z])<=k)
				z++;  
			if(z<y)             //左边的元素大于k，移动右边
			{
				D[y]=D[z];
			}

		} while(z!=y);
		D[z]=k;

		sort(D,start,z-1);
		sort(D,z+1,end);
	}
}



void M_DP::outputNoisyCounts_M_StructureFirst(vector<double>& counts, 
								  double epsilon1, double epsilon2, ofstream& o_file,MTRand& temp_rand){
	run(counts);
	vector<int> boundary;
	boundary = adjustBoundary(counts, epsilon1,temp_rand);
	if((boundary.size() == counts.size() + 1) || (boundary.size() == 2))
		epsilon2 = epsilon1 + epsilon2;
	for(vector<int>::size_type i = 0; i < boundary.size() - 1; i ++){
		const vector<double>& leaves = boost(counts, boundary[i], boundary[i+1], epsilon2, temp_rand);
		for(vector<int>::size_type j = 0; j < leaves.size(); j ++){
			o_file<<leaves[j]<<" ";
		}
	}
	o_file<<endl;
}

vector<int> M_DP::adjustBoundary(vector<double>& hist, double epsilon1,MTRand& temp_rand){
	vector<int> boundary = collParStra();
	if((boundary.size() == hist.size() + 1) || (boundary.size() == 2)){
		return boundary;
	}
	int k = K - 1;
	for(int i = (int)(boundary.size())-1; i > 1; i --){
		vector<int> vectorJ;
		vector<double> vectorPj;
		vector<double> vectorEj;
		int right = boundary[i];
		int left = k;
		double sum = 0.0;
		double minEj = FLT_MAX;

		for(int j = left; j < right; j ++){ 
			double Ej = SAEStar[j-1][k-1] + calSAE(j, right-1, hist);
			vectorJ.push_back(j);
			vectorEj.push_back(Ej);
			if(Ej < minEj)
				minEj = Ej;
		}

		for(vector<int>::size_type x = 0; x < vectorEj.size(); x ++){
			vectorEj[x] -= minEj;
			double powerValue =(-1.0 * epsilon1 * vectorEj[x])/(2.0 * (K-1));
			double Pj = pow(E, powerValue);
			vectorPj.push_back(Pj);
			sum += Pj;
		}

		for(vector<int>::size_type x = 0; x < vectorPj.size(); x ++)
			vectorPj[x] /= sum;

		//MTRand temp_rand;
		//temp_rand.seed();
		double randValue = temp_rand.rand();

		sum = 0.0;
		int chooseIndex;
		for(unsigned int x = 0; x < vectorPj.size(); x ++){
			sum += vectorPj[x];
			if(randValue <= sum){
				chooseIndex = int(x);
				break;
			}
		}

		boundary[i-1] = vectorJ[chooseIndex];
		k--;
	}

	return boundary;
}


vector<double> M_DP::boost(vector<double>& ori_hist, int begin, int end, double epsilon2,MTRand& temp_rand){
	int fan_out = 2;
	double hay_epsilon = epsilon2;
	if(end == begin + 1){
		double value = ori_hist[begin] + Utilities::getLapNoise((1.0)/epsilon2, temp_rand);
		vector<double> a;
		a.push_back(value);
		return a;
	}

	HTree htree(fan_out, ori_hist, begin, end, hay_epsilon,temp_rand);
	htree.inference();
	return htree.returnLeaves();
}


double M_DP::getOptEps1(int n, int k, double epsilon, double maxF){
	double optEpsilon1;
	double minFunctionValue = FLT_MAX;
	double interval = epsilon / STEP_LEN;
	double tempEpsilon1 = 0 + interval;
	while(tempEpsilon1 < epsilon){
		double v = (2*pow((k-1),3.0))/(tempEpsilon1*(2*(k-1)-tempEpsilon1*n*maxF)) + (2*k)/pow((1-tempEpsilon1),2.0);
		//cout<<v<<endl;

		if(v < minFunctionValue){
			optEpsilon1 = tempEpsilon1;
			minFunctionValue = v;
		}	
		tempEpsilon1 += interval;
	}
	return optEpsilon1;
	// return 0.05;
}
