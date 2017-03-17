#!/bin/bash

echo $#

if [ $# -ne 2 ]; then
   echo "Usage: RunXvfb test_file test_dir"
   echo "       test_file - test python file without path"
   echo "       test_dir - path to test file"
   echo "Script run set test in frame buffer"
   exit 1
fi

# Variables.
TEST_FILE="$1"
TEST_DIR="$2"

# Create X virtual framebuffer to run GUI tests.
Xvfb :1 &
PID=$!

# Run tests.
cd $TEST_FILE
DISPLAY=:1 python3 $TESTFILE
if [[ $? != 0 ]]; then kill $PID; exit 1; fi

kill $PID
