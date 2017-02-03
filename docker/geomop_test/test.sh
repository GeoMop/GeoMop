#!/bin/bash

# Variables.
GIT_DIR=/mnt/GeoMop
TEST_DIR=$GIT_DIR/testing
SRC_DIR=$GIT_DIR/src

# Update/install pip dependencies.
#pip3 install -r $GIT_DIR/requirements-development.txt > /dev/null 2>&1

# Create X virtual framebuffer to run GUI tests.
Xvfb :1 &
PID=$!

useradd -m -s /bin/bash test
echo test:MojeHeslo123 | chpasswd


mkdir -p /var/run/sshd
#/usr/sbin/sshd -D
#sed -i 's/PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config
#sed 's@session\s*required\s*pam_loginuid.so@session optional pam_loginuid.so@g' -i /etc/pam.d/sshd
service ssh restart
sleep 10

# copy ssh key
#mkdir -p -m 700 ~/.ssh
#cp /mnt/ssh/id_rsa ~/.ssh/id_rsa
#chmod 600 ~/.ssh/id_rsa

# copy known hosts
#cp /mnt/ssh/known_hosts ~/.ssh/known_hosts

#echo $USER

#ls -al ~/.ssh/

#ifconfig

ssh test@localhost pwd

# Run tests.
#cd $TEST_DIR/common
#export PYTHONPATH=$SRC_DIR/common
#DISPLAY=:1 py.test
#if [[ $? != 0 ]]; then kill $PID; exit 1; fi

#cd $TEST_DIR/ModelEditor
#export PYTHONPATH=$SRC_DIR/ModelEditor:$SRC_DIR/common:./mock
#DISPLAY=:1 py.test
#if [[ $? != 0 ]]; then kill $PID; exit 1; fi

cd $TEST_DIR/JobPanel
export PYTHONPATH=$SRC_DIR/JobPanel:$SRC_DIR/JobPanel/twoparty/pexpect:/$SRC_DIR/common:./mock
DISPLAY=:1 py.test
if [[ $? != 0 ]]; then kill $PID; exit 1; fi

#cd $TEST_DIR/Analysis
#export PYTHONPATH=$SRC_DIR/Analysis:/$SRC_DIR/common
#DISPLAY=:1 py.test
#if [[ $? != 0 ]]; then kill $PID; exit 1; fi

kill $PID
