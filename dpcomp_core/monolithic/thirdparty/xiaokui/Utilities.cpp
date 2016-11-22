#include "Utilities.h"
#include <fstream>


Utilities::Utilities(void){
}

Utilities::~Utilities(void){
}

void Utilities::tokenize(const string& str,vector<double>& tokens,const string& delimiters){
	// Skip delimiters at beginning.
	string::size_type lastPos = str.find_first_not_of(delimiters, 0);
	// Find first "non-delimiter".
	string::size_type pos  = str.find_first_of(delimiters, lastPos);

	while (string::npos != pos || string::npos != lastPos){
		// Found a token, add it to the vector.
		string _strTmp = str.substr(lastPos, pos - lastPos);
		double _number;
		sscanf(_strTmp.c_str(),"%lf",&_number);
		tokens.push_back(_number);
		// Skip delimiters.  Note the "not_of"
		lastPos = str.find_first_not_of(delimiters, pos);
		// Find next "non-delimiter"
		pos = str.find_first_of(delimiters, lastPos);
	}
}


void Utilities::readFile(const string file_name, vector<double>& histogram){
	ifstream in(file_name.c_str(), ios_base::in);
	if(in == NULL){
		cout << "Error:open data file error.\n";
		getchar();
		exit(0);        
	}
	string str;
	const string delimiters = " ";
	getline(in, str);
	tokenize(str, histogram, delimiters);
}


double Utilities::getLapNoise(double lamda,MTRand& temp_rand){
	//MTRand temp_rand;
	//temp_rand.seed();
	double noise;

	double U = temp_rand.randDblExc() - 0.5;
	if (U >= 0)
		noise = -lamda * log(1 - 2 * U);
	else
		noise =  lamda * log(1 + 2 * U);

	return noise;
}








