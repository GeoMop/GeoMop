#!/bin/bash

CURR_PATH=$(pwd)

cd LayerEditor
export PYTHONPATH=../../src/LayerEditor:../../src/common:./mock
py.test-3

cd $CURR_PATH
