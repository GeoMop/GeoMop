#!/bin/bash

docker run -ti --rm -v "/$HOME:/$HOME" -w "/$(pwd)" -p 127.0.0.1:80:8080 "geomop/jobpanel" bash -l

