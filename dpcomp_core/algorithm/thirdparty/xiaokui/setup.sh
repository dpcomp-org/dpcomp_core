#/bin/sh
rm structFirst.py
rm *.pyc
rm *.so
rm structFirst_wrap.cpp
rm -r build
python setup.py build_ext -b . --swig-cpp

