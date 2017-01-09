%module structFirst

%{
#define SWIG_FILE_WITH_INIT
#include "struct.h"
%}

%include "numpy.i"
%init %{
import_array();
%}

%apply (double* IN_ARRAY1, int DIM1) {(double* oricounts, int n)};
%apply (double* ARGOUT_ARRAY1, int DIM1) {(double* noicounts, int n1)};
%include "struct.h"

%clear (double* oricounts, int n);
