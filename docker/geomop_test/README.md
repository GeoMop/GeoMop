# Dockerfile for GeoMop testing

This docker image has all the necessary dependecies to run GeoMop tests 
(including GUI tests).

It uses:

- Debian 8.4 (Jessie)
- Python 3.4.2
- PyQt 5 with QScintilla, QtWebKit

The container automatically installs/updates pip3 dependencies from the
repository's `requirements-development.txt` file.

## Get the container

After you have installed and configured Docker, run:

```bash
docker pull geomop/test
```

## Running the container

You can run the container with the following command.

```bash
docker run \
  -v /var/lib/jenkins/workspace/GeoMop:/mnt/GeoMop \
  geomop/test \
  /home/geomop/test.sh
```

The `-v` argument mount a git repository with the version for tests. Replace 
`/var/lib/jenkins/workspace/GeoMop` with the path to your repository.

## Modifying test.sh

If you want to change or modify the test suite, edit the `test.sh` file. 
Afterwards, you have to build the docker image again by running the
following command from this directory:

```bash
docker build -t geomop/test .
```

After making sure the new container works as expected, please push the 
new image back to Docker hub.

```bash
docker login
docker push geomop/test
```

If you don't have the priviledges, please contact 
[tomaskrizek](https://github.com/tomaskrizek).
