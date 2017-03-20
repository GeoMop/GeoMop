#!/bin/bash

echo $#

if [ $# -ne 3 ]; then
   echo "Usage: RunXvfb test_file result_file copy_dir"
   echo "       test_file - test python file without path that is in current folder"
   echo "       result_file - xml junit result file"
   echo "       copy_dir - where copy xml junit result file"
   echo "Script run set test in frame buffer and copy result to set folder"
   exit 1
fi

# Variables.
TEST_FILE="$1"
TEST_RESULT_FILE="$2"
COPY_DIR="$3"

# Create X virtual framebuffer to run GUI tests.
Xvfb :1 &
PID=$!

# Run tests.
DISPLAY=:1 python3 $TEST_FILE
RESULT= $?
cp $TEST_RESULT_FILE $COPY_DIR
if [[ $RESULT != 0 ]]; then kill $PID; exit 1; fi

kill $PID
