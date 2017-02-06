#/bin/sh

echo 'Cleaning up old objects'
rm -r build
rm ./cutils/*.pyc
rm ./cutils/cutil.py
rm ./cutils/_cutil.so
rm ./cutils/cutil_wrap.cpp

echo 'Complie the C++ utility library'
python setup.py build_ext -b ./cutils/ --swig-cpp