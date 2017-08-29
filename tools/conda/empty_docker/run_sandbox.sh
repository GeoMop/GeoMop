#!/bin/bash

# Start sandbox as regular user.

set -x
SCRIPT_DIR=`pwd`/${0%/*}

# directory containing whole build process
WORKDIR=$HOME

# name of the development image
BASE_IMAGE=geomop/sandbox_base
WORK_IMAGE=geomop/sandbox

get_dev_dir() 
{
    curr_dir=`pwd`
    project_dir="${curr_dir#${WORKDIR}}"    # relative to 'workspace'
    project_dir="${project_dir#/}"          
    project_dir="${project_dir%%/*}"
    
}

cp_to_docker () {
    source=$1
    target=$D_HOME/$2
    target_file=$D_HOME/$2/${source##*/}
    docker cp $source ${running_cont}:$target
    if ! docker exec ${running_cont} chown $U_ID:$G_ID $target_file
    then    
        docker exec ${running_cont} chown $U_ID:$G_ID $target
    fi        
}

make_work_image () 
{
    U_ID=`id -u`
    G_ID=`id -g`
    UNAME=`id -un`
    GNAME=`id -gn`
    D_HOME="/home/$UNAME"
    chown $U_ID:$G_ID $D_HOME
    ls -l $D_HOME

#    if ! docker images | grep "$WORK_IMAGE" > /dev/null
#    then            
        # setup the container
        pwd_dir=`pwd`
        cd ${SCRIPT_DIR}
        docker build -t ${BASE_IMAGE} . 
        cd $pwd_dir
        running_cont=`docker run -itd -v "${WORKDIR}":"${WORKDIR}" ${BASE_IMAGE}`        
        
        # setup user and group
        docker exec ${running_cont} addgroup --gid $G_ID $GNAME
        docker exec ${running_cont} adduser --home "$D_HOME" --shell /bin/bash --uid $U_ID --gid $G_ID --disabled-password --system $UNAME
        docker exec ${running_cont} chown $U_ID:$G_ID $D_HOME
        
        # add git user
        #docker exec ${running_cont} git config --global user.email "jbrezmorf@gmail.com"
        #docker exec ${running_cont} git config --global user.name "Jan Brezina"
        
        # add git-completion
        #curl https://raw.githubusercontent.com/git/git/master/contrib/completion/git-completion.bash -o .git-completion.bash
        #cp_to_docker .git-completion.bash .
        
        # add bashrc, the prompt in particular        
        #cp_to_docker $WORKDIR/_bashrc_docker .bashrc
                
        # add pmake script
        #docker exec -u $U_ID:$G_ID ${running_cont} mkdir "$D_HOME/bin"
        #cp_to_docker $HOME/bin/pmake bin
        
        # add ssh keys
        #docker exec -u $U_ID:$G_ID ${running_cont} mkdir "$D_HOME/.ssh"
        #docker exec ${running_cont} chown jb:jb $HOME/.ssh
        #cp_to_docker $HOME/.ssh/id_rsa  .ssh
        #cp_to_docker $HOME/.ssh/id_rsa.pub  .ssh
                
        docker stop ${running_cont}
        docker commit ${running_cont}  $WORK_IMAGE        
#    fi    
}


U_ID=`id -u`
G_ID=`id -g`

if [ "$1" == "clean" ]
then
    # remove all containers
    docker stop `docker ps -aq`
    docker rm `docker ps -aq`
    docker rmi $WORK_IMAGE
    exit
elif [ "$1" == "make" ]
then
    # just create the docker image
    make_work_image    
    echo "Sandbox ready."
else
    # interactive shell    
    echo "Switching to docker sandbox!!"
    docker run --rm -it -v "${WORKDIR}":"${WORKDIR}"  -w `pwd` -u $U_ID:$G_ID $WORK_IMAGE bash
fi











