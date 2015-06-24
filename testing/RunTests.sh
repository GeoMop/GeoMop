#!/bin/bash

CURR_PATH=$(pwd)

cd LayerEditor
export PYTHONPATH=../../src/LayerEditor:../../src/lib
py.test-3

cd ../lib
export PYTHONPATH=../../src/lib
py.test-3

cd ModelEditor
export PYTHONPATH=../../src/ModelEditor:../../src/lib
py.test-3

cd $CURR_PATH
