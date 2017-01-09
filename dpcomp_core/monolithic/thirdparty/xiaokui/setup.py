#! /usr/bin/env python

from setuptools import *
#from distutils import sysconfig
import numpy

try:
    numpy_include = numpy.get_include()
except AttributeError:
    numpy_include = numpy.get_numpy_include()

_structFirst = Extension("_structFirst",
                    sources = [
                                "DP.cpp",
                                "HTree.cpp",
                                "M_DP.cpp",
                                "struct.cpp",
                                "Utilities.cpp",
                                "structFirst.i",
                              ],
                    include_dirs = [numpy_include],
                )

setup( name = "structFirst",
       ext_modules = [_structFirst]
       )
