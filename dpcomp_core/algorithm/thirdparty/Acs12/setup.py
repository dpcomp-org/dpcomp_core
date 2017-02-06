from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext
import numpy

ext_modules = [Extension(
    name="cutils",
    sources=["lib/cutils/clustering.c", "lib/cutils_pymod.c"],
        # extra_objects=["fc.o"],  # if you compile fc.cpp separately
    #include_dirs = [numpy.get_include()],  # .../site-packages/numpy/core/include
    language="c"
    #extra_compile_args = ["-fno_inline"]
        # extra_link_args = "...".split()
    )]

setup(
    cmdclass = {'build_ext': build_ext},
    ext_modules = ext_modules
)
