#!/bin/bash

CURR_PATH=$(pwd)

cd JobPanel
export PYTHONPATH=../../src/JobPanel:../../src/JobPanel/twoparty/pexpect:../../src/common:./mock
py.test-3

cd $CURR_PATH
