#!/bin/bash

CURR_PATH=$(pwd)

cd LayerEditor
export PYTHONPATH=../../src/LayerEditor
py.test-3

cd ../lib
export PYTHONPATH=../../src/lib
py.test-3


cd $CURR_PATH
