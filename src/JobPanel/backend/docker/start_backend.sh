BACKEND_PY=/home/jb/workspace/GeoMop/src/JobPanel/jb/backend_service.py

# publishing ports: -p 5000:5000
#docker run  --rm -v /home/jb:/home/jb geomop:backend python3 $BACKEND_PY [0] yy
#docker run  --rm -v /home/jb:/home/jb geomop:backend echo "exec"
docker run  --rm -it -v /home/jb:/home/jb -w /home/jb/workspace/GeoMop/src/JobPanel/jb/ geomop:backend 
