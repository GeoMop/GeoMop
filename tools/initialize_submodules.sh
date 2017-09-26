#!/bin/bash

#  Should be run from Geomop root_dir
git submodule init
origin_url=$$( git config --get remote.origin.url ) ;\
if [ "$${origin_url}" != "$${origin_url#https}" ]; \
then \
    cp .gitmodules_https .gitmodules; \
fi
git submodule sync
git checkout .gitmodules