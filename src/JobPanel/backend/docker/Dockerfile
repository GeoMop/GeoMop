# BASE Dockerfile for running flow123d
FROM ubuntu:16.04
MAINTAINER Jan Brezina

# fix bash
RUN rm /bin/sh && ln -s /bin/bash /bin/sh

# install basic set of tools
RUN apt-get update && apt-get install -y  \
    sudo \
    make \
    wget  \
    python3 \
    python-dev \
    python-pip \
    bash-completion \
    apt-utils \
    vim \
    less \
    man

# install python basic tools
# TODO: reduce for GeoMop purposes
RUN sudo pip install \
    pyyaml \
    markdown \
    psutil \
    simplejson \
    formic
        

# add auto bash-completion load
COPY autoload.sh /etc/profile.d/autoload.sh

# default entrypoint will be login bash
CMD ["/bin/bash", "-l"]


