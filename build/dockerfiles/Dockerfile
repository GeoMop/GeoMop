ARG images_version
ARG base_image
FROM ${base_image} as installer

# missing dependencies in MLMC
RUN python3 -m pip install  --no-cache-dir --ignore-installed \
    h5py \
    ruamel.yaml \
    memoization \
    matplotlib

# install mpi4py with own MPI lib version
RUN env MPICC=$(cat /.mpiccpath) python3 -m pip install --no-cache-dir --ignore-installed  \
   mpi4py 

# GeoMop packages
RUN python3 -m pip install  --no-cache-dir --ignore-installed \
   bgem \
   mlmc \
   visip

COPY version.yml /geomop_version.yml
   
