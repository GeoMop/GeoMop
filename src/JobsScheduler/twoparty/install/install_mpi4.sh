#!/bin/bash
#%A
#Usage:
#======
##install_mpi4.sh interpreter
#
#Script start mpi4 install process. Script is necessary 
#start from home folder
#Parameters:
#  interpreter - Command for perl interpreter
#Example:
##install_mpi4.sh /opt/python/bin/python3.3
#%B

function print_help() {
	sed -ne '/#%A/,/#%B/s/\(^#\|^#%[AB]\)//p' $0
}

if [ $# -lt 1 ] ; then print_help 1>&2; exit 1; fi
if [[ "$*" =~ -h ]] ; then print_help; exit 0; fi

INTERPRETER=$1  

TAR_FILE=mpi4py-2.0.0.tar.gz
BUILD_DIR=mpi4py-2.0.0
CURR_PATH=$(pwd)

tar -zxf $TAR_FILE
cd $BUILD_DIR
$INTERPRETER setup.py build
$INTERPRETER setup.py install --install-lib=../../../ins-lib

cd $CURR_PATH
rm -rf $BUILD_DIR
