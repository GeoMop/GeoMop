#!/bin/bash

CURR_PATH=$(pwd)

cd JobPanel
export PYTHONPATH=../../src/JobPanel:../../src/JobPanel/twoparty/pexpect:../../src/common:../../src/JobPanel/twoparty/pexpect:./mock
py.test-3

cd $CURR_PATH
