#!/bin/bash

#initialize submodules
cp .gitmodules_https .gitmodules
git submodule init
git submodule update
git submodule sync
git checkout .gitmodules

# install geomop
bash ./tools/meta_install/install.sh ../geomop_root
