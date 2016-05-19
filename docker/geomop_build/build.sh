#!/bin/bash

GITSRC=/mnt/GeoMop
GITTMP=/home/geomop/GeoMop

# Copy the git repo.
cp -rf $GITSRC/* $GITTMP/
cp -rf $GITSRC/.[^.]* $GITTMP/

# Update/install pip3 dependencies.
pip3 install -r $GITTMP/requirements-development.txt > /dev/null 2>&1

# Clean the dist directory.
rm -rf $GITTMP/dist/*

# Update VERSION and create debian package.
cd $GITTMP/build
make debian
if [[ $? != 0 ]]; then echo "Debian build failed."; exit 1; fi

# Create Windows installer.
cd $GITTMP
makensis win_x86.nsi

# Clean and copy the dist directory.
rm -rf $GITSRC/dist/*
cp -rf $GITTMP/dist/* $GITSRC/dist/

