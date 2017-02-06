#! /usr/bin/env python

from setuptools import *
#from distutils import sysconfig
import numpy

try:
    numpy_include = numpy.get_include()
except AttributeError:
    numpy_include = numpy.get_numpy_include()

_cutil = Extension("_cutil",
                    sources = ["./cutils/mtrand.cpp", "./cutils/cutil.i", "./cutils/cutil.cpp"],
                    include_dirs = [numpy_include],
                )

setup( name = "cutil",
       description = "",
       author = "",
       version = "0.1",
       extras_require = {
       'np':['numpy>=1.9.1'],
       'cp':['scipy>=0.11.0'],
       },
       ext_modules = [_cutil]
       )
