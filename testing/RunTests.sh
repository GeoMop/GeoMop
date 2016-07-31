#!/bin/bash

CURR_PATH=$(pwd)

cd LayerEditor
export PYTHONPATH=../../src/LayerEditor:../../src/common
py.test-3

cd ../common
export PYTHONPATH=../../src/common
py.test-3

cd ../ModelEditor
export PYTHONPATH=../../src/ModelEditor:../../src/common:./mock
py.test-3

cd ../JobsScheduler
export PYTHONPATH=../../src/JobsScheduler:../../src/common:../../src/JobsScheduler/twoparty/pexpect:./mock
py.test-3

cd ../Analysis
export PYTHONPATH=../../src/Analysis:../../src/common
py.test-3

cd $CURR_PATH
