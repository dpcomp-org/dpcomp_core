// Utilities.h
// Implemented by Jia XU
// 2011-05
// A class to define the utility functions

#pragma  once
#include <cstdlib>
#include <vector>
#include <iostream>
#include <string>
#include <fstream>
#include <limits>
#include "MersenneTwister.h"
using    namespace std;


#define  E        2.71828183
#define  K_RATIO  0.1     /// is used to set k based on the cardinality of data set in StructureFirst
#define  STEP_LEN 20        /// sample length in selecting optimal epsilon1


struct Histogram{
	Histogram(){
	}
	Histogram(int bin_num){
		counts.resize(bin_num, 0);
	}
	vector<double> counts;
	vector<int> partition;
};


class Utilities
{
public:
	Utilities(void);
	~Utilities(void);
	static void tokenize(const string& str,vector<double>& tokens,const string& delimiters);
    static void readFile(const string file_name, vector<double>& histogram);
    static double getLapNoise(double lamda,MTRand& temp_rand);

};
