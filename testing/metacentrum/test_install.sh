#!/bin/bash
SCRIPTPATH="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

#initialize submodules
cp .gitmodules_https .gitmodules
git submodule init
git submodule update
git submodule sync
git checkout .gitmodules

# install geomop
bash ${SCRIPTPATH}/install.sh ../geomop_root
