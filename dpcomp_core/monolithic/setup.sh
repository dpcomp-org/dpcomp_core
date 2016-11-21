#/bin/sh

echo 'Cleaning up old objects'
rm -r build
rm ./cutils/*.pyc
rm ./cutils/cutil.py
rm ./cutils/_cutil.so
rm ./cutils/cutil_wrap.cpp

echo 'Complie the C++ utility library'
python setup.py build_ext -b ./cutils/ --swig-cpp

echo 'Setup Thirdparty packages'
cd ./thirdparty

echo ' -- Acs12'
cd Acs12
./setup.sh
cd ..

echo ' -- xiaokui'
cd xiaokui
./setup.sh
cd ..

cd ..
