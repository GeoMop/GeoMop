FROM flow123d/v2.1.0:user

RUN apt-get update && apt-get install -y \
  python3-pip \
  python3-paramiko \
&& pip3 install \
  Markdown==2.6.2 \
  PyYAML==3.11 \
  six==1.10.0 \
  numpy==1.12.0 \
  scipy==0.18.1 \
  psutil \
  pydes
