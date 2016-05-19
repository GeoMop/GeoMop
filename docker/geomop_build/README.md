# Dockerfile for GeoMop testing

This Docker machine builds Windows and debian install packages for GeoMop.

The container containes the necessary dependecies for the Windows runtime
environment. If you want to modify or update them, you can find them in
the `build` folder on our [Jenkins](http://ci3.nti.tul.cz) server. After making a new
image, please push it back to the Docker hub as explained below.

The image uses NSIS 3.0 rc1 to generate the Windows installer.

## Get the container

After you have installed and configured Docker, run:

```bash
docker pull geomop/build
```

## Running the container

You can run the container with the following command.

```bash
docker run \
  -v /var/lib/jenkins/workspace/GeoMop:/mnt/GeoMop \
  geomop/build \
  bin/bash -c " \
    /home/geomop/build.sh; \
    chown -R $(id -u):$(id -g) /mnt/GeoMop \
  "
```

The `-v` argument mount a git repository with the version for tests. Replace 
`/var/lib/jenkins/workspace/GeoMop` with the path to your repository.

After the `build.sh` script is has completed, file ownership is modified
to match the current user (since Docker uses different user ids).

You can find the installation packages in `dist/` directory of the repository
you specified. Please note that the `build.sh` script deletes all files in 
this location prior to creating the new ones.

## Modifying build.sh / adding dependencies

You can only modify the image if you have the `build/` and `lib/` directory 
dependecies. These are not tracked in github. They can be found on the
[Jenkins](http://ci3.nti.tul.cz) server. Please contact 
[tomaskrizek](https://github.com/tomaskrizek) for more information.

If you want to change or modify the build process, edit the `build.sh` file. 
Afterwards, you have to build the docker image again by running the
following command from this directory:

```bash
docker build -t geomop/build .
```

After making sure the new container works as expected, please push the 
new image back to Docker hub.

```bash
docker login
docker push geomop/build
```

If you don't have the priviledges, please contact 
[tomaskrizek](https://github.com/tomaskrizek).


## Maintainer Info

Docker directory on Jenkins: `/home/geomop/docker/geomop_build`

The `build` and `lib` directories contain the necessary files to build Windows
installer. DO NOT REMOVE them in case you need to build the docker image. 
These files are not tracked in git.
