#!/bin/bash

echo "************ RUNNING TESTS *************"

# test
docker run \
  --net=host \
  -v /home/geomop/.ssh:/home/geomop/.ssh \
  -v /var/lib/jenkins/workspace/GeoMop:/mnt/GeoMop \
  geomop/test \
  /home/geomop/test.sh
if [[ $? != 0 ]]; then exit 1; fi

#-v /home/geomop/.ssh:/home/geomop/.ssh \

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
