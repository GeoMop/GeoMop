#!/bin/bash

# We assume installed Python 3.4 or 3.5 or 3.6 and pip3.
# To force new installation remove $HOME/miniconda3

set -x

conda_dir=$HOME/miniconda3
if [ ! -d "${conda_dir}"  ]
then
    # download
    if [ ! -f "./Miniconda3-latest-Linux-x86_64.sh" ]
    then
        wget http://geomop.nti.tul.cz/libraries/Miniconda3-latest-Linux-x86_64.sh
    fi
    
    # install
    chmod u+x ./Miniconda3-latest-Linux-x86_64.sh
    ./Miniconda3-latest-Linux-x86_64.sh -b -p $conda_dir
fi    