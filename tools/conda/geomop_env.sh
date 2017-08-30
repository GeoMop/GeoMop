#!/bin/bash

# Creates conda environment 'geomop_dev' for GeoMop development
# - install necessary python packages using pip
# - install OCC
# - install netgen
#
# Switch to the environment:
# > source activate geomop_dev
#
# Leave the environment:
# > source deactivate
#

#set -x

PATH=$PATH:$HOME/miniconda3/bin
SCRIPT_DIR=`pwd`/${0%/*}
conda_dir=$HOME/miniconda3


get_file() {
    file=${1##*/}
    prefix="${1%/*}/"
    if [ "$prefix" == "" ]
    then
        prefix="./"
    fi
    if [ ! -f "$1" ]
    then
        wget -P "$prefix" "http://geomop.nti.tul.cz/libraries/$file"
    fi    
}


install_miniconda() {
    if [ ! -d "${conda_dir}"  ]
    then
        # download
        get_file ./Miniconda3-latest-Linux-x86_64.sh
        
        # install
        chmod u+x ./Miniconda3-latest-Linux-x86_64.sh
        ./Miniconda3-latest-Linux-x86_64.sh -b -p $conda_dir
    fi    
}



safe_env_create()
{
    env_name=$1
    shift    
    if ! conda env list | grep "$env_name"
    then
        echo "Creating environment: $env_name"
        conda create -y --name $env_name $@
    fi    
}



clean_envs() {   
    conda remove -n pythonocc --all
    conda remove -n geomop_dev --all
    conda remove -n pythonocc_dev --all
    conda remove -n devel_base --all
}


netgen_build_pkg() 
{
    # Prepare netgen package for conda.
    pwd_dir=`pwd`
    cd $SCRIPT_DIR
    
    # download build recepies bundle (from tpaviot/netgen-conda repository)
    if [ ! -d "netgen-conda" ]
    then
        get_file netgen-conda.tgz
        tar -xzf netgen-conda.tgz    
    fi
    conda build --prefix-length 70  -c salford_systems -c conda-forge -c dlr-sc netgen-conda/netgen-6.2-dev 
    
    # Package is created at: $HOME/miniconda3/conda-bld/linux-64/netgen-6.2.dev-*.tag.bz2
    # currently we uplad it manually to Bacula
}


geomop_dev_env()
{
    
    # Create conda environment 'geomop_dev' for the GeoMop development.    
    ENV_NAME=geomop_dev
    safe_env_create $ENV_NAME 
    source activate $ENV_NAME
    
    conda install -y -c conda-forge -c dlr-sc oce python==3.5
    
    # Netgen
    # Curently we rebuild the package if it is not found until we
    # manage to have own Anaconda repository for these packages.
    if ! conda search --use-local | grep netgen
    then
        netgen_build_pkg
    fi
    conda install --use-local -y netgen
    
    source deactivate
}


if [ "$1" == "clean-all" ]
then
    clean_env
    exit
elif [ "$1" == "netgen-pkg" ]
then    
    netgen_build_pkg 
    exit
elif [ "$1" == "miniconda" ]
then
    install_miniconda
    exit
elif [ "$1" == "geomop_env" ]
then
    geomop_dev_env
    exit
else
    cat <<END-help
Usage: geomop_env.sh <command>
    
Commands:    
    miniconda       Install miniconda tool.
    geomop_env      Creates the 'geomop' environment containing necessary Python packages (including oce and netgen).
    netgen-pkg      Build the netgen package. Has to be uploaded to Bacula manually.
    clean-all       Remove all conda environments created by this script.
END-help

fi



