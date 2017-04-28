#!/bin/bash

if $TESTS; then

echo "************ RUNNING TESTS *************"

# test
docker run \
  -v /var/lib/jenkins/workspace/gm-build:/mnt/GeoMop \
  geomop/test \
  /home/geomop/test.sh
if [[ $? != 0 ]]; then exit 1; fi

fi


echo "************ RUNNING BUILD *************"

# clear results
rm -rf /var/lib/jenkins/workspace/gm-build/dist
mkdir /var/lib/jenkins/workspace/gm-build/dist

# build
docker run \
  -v /var/lib/jenkins/workspace/gm-build:/mnt/GeoMop \
  -e VERSION=$VERSION \
  geomop/build \
  bin/bash -c " \
    /home/geomop/build.sh; \
    chown -R $(id -u):$(id -g) /mnt/GeoMop \
  "
if [[ $? != 0 ]]; then exit 1; fi

echo "************** SUCCESS ****************"

exit 0
