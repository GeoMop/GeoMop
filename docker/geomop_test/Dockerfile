FROM debian:jessie

RUN apt-get update && apt-get install -y \
  python3-pip \
  python3-pyqt5 \
  python3-pyqt5.qsci \
  python3-pyqt5.qtwebkit \
  openssh-client \
  xvfb  # Used for a virtual X server framebuffer to run GUI tests.

ENV HOME_DIR /home/geomop
ENV GITSRC /mnt/GeoMop

# Create directories
RUN mkdir -m 777 $HOME_DIR
RUN mkdir -m 777 $GITSRC
RUN mkdir -m 777 /mnt/ssh
#RUN mkdir -p -m 700 ~/.ssh

# Copy test script
COPY test.sh $HOME_DIR/
