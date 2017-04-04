FROM flow123d/v2.1.0:user

RUN apt-get update && apt-get install -y \
  python3-pip \
  openssh-client \
  python3-pyqt5 \
  python3-pyqt5.qsci \
  python3-pyqt5.qtwebkit \
  xvfb  # Used for a virtual X server framebuffer to run GUI tests.

RUN pip3 install Markdown==2.6.2
RUN pip3 install PyYAML==3.11
RUN pip3 install py==1.4.30
RUN pip3 install Pygments==2.0.2
RUN pip3 install pylint==1.4.4
RUN pip3 install pytest
RUN pip3 install six==1.10.0
RUN pip3 install Sphinx==1.3.1
RUN pip3 install sphinx-rtd-theme==0.1.9
RUN pip3 install numpydoc==0.6.0
RUN pip3 install numpy==1.12.0
RUN pip3 install scipy==0.18.1

