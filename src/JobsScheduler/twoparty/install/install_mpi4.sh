#!/bin/bash

TAR_FILE=mpi4py-2.0.0.tar.gz
BUILD_DIR=mpi4py-2.0.0
CURR_PATH=$(pwd)

tar -zxf $TAR_FILE
cd $BUILD_DIR
python3 setup.py build
python3 setup.py install --install-lib=../../../ins-lib

cd $CURR_PATH
