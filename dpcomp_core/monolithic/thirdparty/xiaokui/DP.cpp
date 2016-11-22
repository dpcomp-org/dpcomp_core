#include "DP.h"


DP::DP(int _N, int _B){
	N = _N;
	K = _B;
	P.resize(_N);
	PP.resize(_N);
	vector<double> doubleT(_B, FLT_MAX);
	vector<int> intT(_B, INT_MAX);
	SSEStar.resize(_N, doubleT);
	solution.resize(_N, intT);
}


DP::DP(){
}

DP::~DP(void){
}



void DP::initialPara(vector<double>& hist){
	P[0] = hist[0];
	PP[0] = pow(hist[0], 2);
	for(int i = 1; i < N; i ++){
		P[i] = P[i-1] + hist[i];
		PP[i] = PP[i-1] + pow(hist[i], 2);
	}
	for(int i = 0; i < K; i ++)
		solution[i][i] = i;
}


///use initialPara before calSSE
double DP::calSSE(int i, int j){
	if(i == j)
		return 0.0;

	double SSE_ij = PP[j] - PP[i-1] - pow(P[j] - P[i-1], 2) / (j - i + 1);
	return SSE_ij;
}


void DP::innerLoop(int startIndex, int i, int k){
	double minDist = FLT_MAX;
	for(int j = startIndex; j < i; j ++){
		double tempSSE = SSEStar[j][k-1] + calSSE(j+1, i);///+noise;
		if(tempSSE < minDist){
			solution[i][k] = j + 1;
			SSEStar[i][k] = tempSSE;
			minDist = tempSSE;
		}
	}
}

void DP::run(vector<double>& hist){
	initialPara(hist);
	for(int i = 0; i < K; i ++){
		SSEStar[i][i] = 0;
		solution[i][i] = i;
	}

	for(int i = 1; i < N; i ++){
		double avg = P[i] / (i + 1);
		double differ = 0.0;
		for(int j = 0; j <= i; j ++){
			double v = fabs(hist[j] - avg);
			differ += v * v; 
		}
		SSEStar[i][0] = differ;	
		solution[i][0]=0;
	}

	for(int k = 1; k < K; k ++){
		for(int i = k + 1; i < N; i ++){
			innerLoop(k - 1, i, k);
		}
	}
}


vector<int> DP::adjustBoundery(vector<double>& hist, double epsilon1, double maxF, MTRand& temp_rand){
	vector<int> boundery = collParStra();
	if((boundery.size() == hist.size() + 1) || (boundery.size() == 2)){
		return boundery;
	}
	int k = K - 1;
	for(int i = (int)(boundery.size())-1; i > 1; i --){
		vector<int> vectorJ;
		vector<double> vectorPj;
		vector<double> vectorEj;
		int right = boundery[i];
		int left = k;
		int toMove = boundery[i-1];
		double sum = 0.0;
		double minEj = FLT_MAX;

		for(int j = left; j < right; j ++){ 
			double Ej = SSEStar[j-1][k-1] + calSSE(j, right-1);
			vectorJ.push_back(j);
			vectorEj.push_back(Ej);
			if(Ej < minEj)
				minEj = Ej;
		}

		for(vector<int>::size_type x = 0; x < vectorEj.size(); x ++){
			vectorEj[x] -= minEj;
			double powerValue =(-1.0 * epsilon1 * vectorEj[x])/(2.0 * (K) * (2 * maxF + 1));
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

		boundery[i-1] = vectorJ[chooseIndex];
		k--;
	}

	return boundery;
}

vector<int> DP:: collParStra(){
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

	return boundary;
}


void DP::outputNoisyCounts_StructureFirst(vector<double>& counts, vector<double>& cutCounts, 
								  double epsilon1, double epsilon2, double maxF, vector<double>& ovec, MTRand& temp_rand){
    int ct = 0;
	run(cutCounts);
	vector<int> boundery = adjustBoundery(cutCounts, epsilon1, maxF, temp_rand);///use \epsilon_1 budget
	if((boundery.size() == counts.size() + 1) || (boundery.size() == 2))
		epsilon2 = epsilon1 + epsilon2;
	for(vector<int>::size_type i = 0; i < boundery.size() - 1; i ++){
		const vector<double>& leaves = boost(counts, boundery[i], boundery[i+1], epsilon2,temp_rand);
		for(vector<int>::size_type j = 0; j < leaves.size(); j ++){
			//o_file<<leaves[j]<<" ";
            ovec[ct++] = leaves[j];
		}
	}
	//o_file<<endl;
}


void DP::outputNoisyCounts_NoiseFirst(Histogram& noisyHist, double epsilon, ofstream& o_file){
	run(noisyHist.counts);
	noisyHist.partition = collParStra();
	for(vector<int>::size_type i = 0; i < noisyHist.partition.size() - 1; i ++){
		addNoise2Partition(noisyHist.counts, noisyHist.partition[i], noisyHist.partition[i+1], epsilon, o_file);
	}
	o_file<<endl;
}


void DP::addNoise2Partition(vector<double>noisyHist, int begin, int end, double epsilon, ofstream& o_file){
	if(end == begin + 1){
		o_file<<noisyHist[begin]<<" ";
		return;
	}

	int n = end - begin;
	double mergeEstimateError, dworkEstimateError;

	double avg = 0;
	for(int i = begin; i < end; i ++){
		avg += noisyHist[i];
	}
	avg /= n;

	double HbarDbar_merge = 0;
	for(int i = begin; i < end; i ++){
		HbarDbar_merge += pow(fabs(avg - noisyHist[i]), 2.0);
	}
	mergeEstimateError = HbarDbar_merge - ((2.0)*(n-2))/(epsilon*epsilon);
	dworkEstimateError = ((2.0)*n)/(epsilon*epsilon);

	if(mergeEstimateError > dworkEstimateError){
		for(int i = begin; i < end; i ++)
			o_file<<noisyHist[i]<<" ";
	}else{
		for(int i = begin; i < end; i ++)
			o_file<<avg<<" ";
	}
}

vector<double> DP::boost(vector<double>& ori_hist, int begin, int end, double epsilon2,MTRand& temp_rand){
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


int DP::findOptK(vector<double>& hist, double epsilon){
	int optK;
	initialPara(hist);

	for(int i = 0; i < K; i ++)
		SSEStar[i][i] = 0;

	for(int i = 1; i < N; i ++){
		double avg = P[i] / (i + 1);
		double differ = 0;
		for(int j = 0; j <= i; j ++){
			double v = fabs(hist[j] - avg);
			differ += v * v; 
		}
		SSEStar[i][0] = differ;
	}

	for(int k = 1; k < K; k ++){
		for(int i = k + 1; i < N; i ++){
			double minDist = FLT_MAX;
			innerLoop(k - 1, i, k);
		}
	}

	double minValue = FLT_MAX;

	for(int i = 0; i < K; i ++){
		double estimatedErr = SSEStar[N-1][i] - (2.0*(N-2.0*(i+1)))/(pow(epsilon,2.0));
		if(estimatedErr < minValue){
			minValue = estimatedErr;
			optK = i+1;
		}
	}
	return optK;
}



double DP::getOptEps1(int n, int k, double epsilon, double maxF){
	double optEpsilon1;
	double minFunctionValue = FLT_MAX;
	double interval = epsilon / STEP_LEN;
	double tempEpsilon1 = 0 + interval;
	while(tempEpsilon1 < epsilon){
		double v = (8*(k-1)*(k-1)*pow((2*maxF+1),2.0))/(tempEpsilon1*(8*(k-1)*(2*maxF+1)-tempEpsilon1*n*pow(maxF,2.0)))
			+((2.0)*k) / (pow(epsilon-tempEpsilon1, 2.0));
		if(v < minFunctionValue){
			optEpsilon1 = tempEpsilon1;
			minFunctionValue = v;
		}	
		tempEpsilon1 += interval;
	}
	return optEpsilon1;
}



