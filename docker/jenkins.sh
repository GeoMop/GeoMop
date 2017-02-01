#!/bin/bash

echo "************ RUNNING TESTS *************"

# test
docker run \
  --net=host \
  -v /var/lib/jenkins/workspace/GeoMop:/mnt/GeoMop \
  -v /home/geomop/.ssh:/mnt/ssh \
  geomop/test \
  /home/geomop/test.sh
if [[ $? != 0 ]]; then exit 1; fi

#-v /home/geomop/.ssh:/home/geomop/.ssh \
#--net=host \
#-p 22:22 \

echo "************ RUNNING BUILD *************"

# build
docker run \
  -v /var/lib/jenkins/workspace/GeoMop:/mnt/GeoMop \
  -e VERSION=$VERSION \
  geomop/build \
  bin/bash -c " \
    /home/geomop/build.sh; \
    chown -R $(id -u):$(id -g) /mnt/GeoMop \
  "
if [[ $? != 0 ]]; then exit 1; fi

echo "************** SUCCESS ****************"

exit 0
