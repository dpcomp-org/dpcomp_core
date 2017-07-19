#/bin/sh

rm ./lib/*.so
rm ./lib/*.pyc
rm -r build
python setup.py build_ext -b ./lib/

