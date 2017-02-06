#include "clustering.h"
#include <math.h>


static double l1_mean(double* x, int start, int end)
{ 
    double result = 0.;
    int i;
    for (i = start; i < end; i++) result += x[i];
    result /= (end - start);
    return result;
}

double l1_distance(double* vec, int start, int end, double avg)
{
	double dist = 0.;
	int i;

	for (i = start; i < end; i++) 
	{
	   dist += fabs(vec[i] - avg);
	}

	return dist;
}

item_t clustersplit(double* list, int pos, int size)
{
        item_t ret;

        ret.c1 = l1_mean(list, 0, pos);
        ret.c2 = l1_mean(list, pos, size);
        ret.error = l1_distance(list, 0, pos, ret.c1) +  l1_distance(list, pos, size, ret.c2);

        return ret;
       
}

