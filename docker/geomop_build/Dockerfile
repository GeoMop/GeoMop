FROM debian:jessie

RUN apt-get update && apt-get install -y \
  build-essential \
  debhelper \
  devscripts \
  fakeroot \
  g++ \
  gcc \
  git \
  python3-pip \
  scons \
  zlib1g \
  zlib1g-dev \
  zlibc

ENV HOME /home/geomop
ENV GITSRC /mnt/GeoMop
ENV GITTMP /home/geomop/GeoMop


# Install NSIS
COPY lib/nsis-3.0rc1-src/ /usr/local/nsis/nsis-3.0rc1-src
COPY lib/nsis-3.0rc1/ /usr/local/nsis/nsis-3.0rc1

# Compile nsis
RUN cd /usr/local/nsis/nsis-3.0rc1-src && scons SKIPSTUBS=all SKIPPLUGINS=all \
  SKIPUTILS=all SKIPMISC=all NSIS_CONFIG_CONST_DATA=no \
  PREFIX=/usr/local/nsis/nsis-3.0rc1 install-compiler

# Create makensis link
RUN cd /usr/bin && ln -s /usr/local/nsis/nsis-3.0rc1/bin/makensis makensis

# Fix zlib missing error
RUN mkdir /usr/local/nsis/nsis-3.0rc1/share && \
  cd /usr/local/nsis/nsis-3.0rc1/share && \
  ln -s /usr/local/nsis/nsis-3.0rc1 nsis


# Create directories
RUN mkdir -m 777 $HOME
RUN mkdir -m 777 -p $GITTMP/dist
RUN mkdir -m 777 -p $GITTMP/build/win_x86
RUN mkdir -m 777 $GITSRC

# Copy Windows dependencies
COPY build/win_x86 $GITTMP/build/win_x86

# Copy build script
COPY build.sh $HOME/
