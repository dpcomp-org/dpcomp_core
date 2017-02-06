%module cutil

%{
#define SWIG_FILE_WITH_INIT
#include "cutil.h"
%}

%include "numpy.i"
%init %{
import_array();
%}

%apply (double* IN_ARRAY1, int DIM1) {(double* x, int n)};
%apply (int* ARGOUT_ARRAY1, int DIM1) {(int* hist, int n1)};
%include "cutil.h"

%clear (double* x, int n);
