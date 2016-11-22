/*
@author: Gergely Acs <acs@crysys.hu>
*/

#include "Python.h"
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include "cutils/clustering.h"

/* Must define Py_TYPE for Python 2.5 or older */
#ifndef Py_TYPE
#  define Py_TYPE(o) ((o)->ob_type)
#endif

/* Must define PyVarObject_HEAD_INIT for Python 2.5 or older */
#ifndef PyVarObject_HEAD_INIT
#define PyVarObject_HEAD_INIT(type, size)       \
        PyObject_HEAD_INIT(type) size,
#endif

/* ========================================================================== */
/* -- Methods --------------------------------------------------------------- */
/* ========================================================================== */


static PyObject* py_l1distance(PyObject* self, PyObject* args)
{
  PyObject* DATA = NULL;
  PyObject* item = NULL;
  double* data = NULL;
  Py_ssize_t data_len;
  double avg;
  Py_ssize_t i;
  PyObject* num; 

  if (!PyArg_ParseTuple(args, "Od", &DATA, &avg))
        return NULL;

  data_len = PyObject_Length(DATA);
  data = (double *)malloc(sizeof(double)*data_len);

  for (i = 0; i < data_len; i++) 
  {
    item = PySequence_GetItem(DATA, i);
    data[i] = PyFloat_AsDouble(item);
    Py_DECREF(item);
  }

  num = PyFloat_FromDouble(l1_distance(data,0,(int)data_len,avg));
  if (!num) 
    return NULL;
  // printf("i: %d err: %.4f\n",i,error);
  free(data);

  //return splits;
  return num;
}



static PyObject* py_clustersplit(PyObject* self, PyObject* args)
{
  PyObject* DATA = NULL;
  PyObject* item = NULL;
  double* data = NULL;
  Py_ssize_t data_len;
  Py_ssize_t i;
  PyObject* splits; 
  PyObject* c1; 
  PyObject* c2; 
  PyObject* num; 
  item_t split;

  if (!PyArg_ParseTuple(args, "O", &DATA))
        return NULL;

  data_len = PyObject_Length(DATA);
  data = (double *)malloc(sizeof(double)*data_len);

  splits = PyList_New(data_len-1);

  if (splits == NULL)
  	return NULL;

  for (i = 0; i < data_len; i++) 
  {
    item = PySequence_GetItem(DATA, i);
    data[i] = PyFloat_AsDouble(item);
    Py_DECREF(item);
  }

  for (i = 1; i < data_len; i++) 
  {
      split = clustersplit(data,(int)i,(int)data_len);
      num = PyFloat_FromDouble(split.error);
      c1 = PyFloat_FromDouble(split.c1);
      c2 = PyFloat_FromDouble(split.c2);
      if (!num) 
      {
        Py_DECREF(splits);
        return NULL;
      }
      item = PyList_New(3);
      PyList_SET_ITEM(item, 0, num); 
      PyList_SET_ITEM(item, 1, c1); 
      PyList_SET_ITEM(item, 2, c2); 
      PyList_SET_ITEM(splits, i-1, item);  
      // printf("i: %d err: %.4f\n",i,error);
  }
  free(data);

  return splits;
}

/* ========================================================================== */
/* -- The methods table ----------------------------------------------------- */
/* ========================================================================== */


static char split__doc__[] =
"compute the error of all possible splits for a given array\n";


static struct PyMethodDef cutils_methods[] = {
   {"clustersplit", (PyCFunction) py_clustersplit, METH_VARARGS, split__doc__},
   {"l1distance", (PyCFunction) py_l1distance, METH_VARARGS, ""},
   {NULL,          NULL, 0, NULL}/* sentinel */
};

/* ========================================================================== */
/* -- Initialization -------------------------------------------------------- */
/* ========================================================================== */


void
initcutils(void)
{
    PyObject *m;

    m = Py_InitModule("cutils", cutils_methods);
    if (m == NULL)
        return;

    PyObject* cutils_error = PyErr_NewException("cutils.error", NULL, NULL);
    Py_INCREF(cutils_error);
    PyModule_AddObject(m, "error", cutils_error);
}
