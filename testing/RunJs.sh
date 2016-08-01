#!/bin/bash

CURR_PATH=$(pwd)

cd JobsScheduler
export PYTHONPATH=../../src/JobsScheduler:../../src/JobsScheduler/twoparty/pexpect:../../src/common:../../src/JobsScheduler/twoparty/pexpect:./mock
py.test-3

cd $CURR_PATH
