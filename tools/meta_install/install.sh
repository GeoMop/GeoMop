#!/bin/bash
# Script will install GeoMop on Metacentrum


# get absolute dir in which is this script stored
CWD="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"


function usage {
    echo "Install GeoMop to specified directory."
    echo "Usage: install.sh GEOMOP_ROOT_DIR EXECUTABLE_1_NAME EXECUTABLE_1_PATH EXECUTABLE_2_NAME EXECUTABLE_2_PATH ..."
    exit
}

num_par=$#
if [[ $((num_par%2)) -eq 0 ]]; then
    usage
    exit
fi


# GeoMop root directory
GEOMOP_INST="$( realpath "$1" )"


mkdir -p "$GEOMOP_INST"


echo "Creating virtual environment..."
rm -rf "$GEOMOP_INST/env"
module add python-3.6.2-gcc python36-modules-gcc
python -m venv "$GEOMOP_INST/env"


echo "Upgrading pip..."
# Don't working
#"$GEOMOP_INST/env/bin/pip" install --upgrade pip
"$GEOMOP_INST/env/bin/easy_install" -U pip


echo "Instaling python packages..."
"$GEOMOP_INST/env/bin/pip" install psutil
"$GEOMOP_INST/env/bin/pip" install PyYAML
"$GEOMOP_INST/env/bin/pip" install paramiko
"$GEOMOP_INST/env/bin/pip" install numpy
"$GEOMOP_INST/env/bin/pip" install scipy


echo "Copying GeoMop modules..."
SRC="$CWD/../../src"
cp -r "$SRC/gm_base" "$GEOMOP_INST"
cp -r "$SRC/JobPanel" "$GEOMOP_INST"
cp -r "$SRC/Analysis" "$GEOMOP_INST"


echo "Creating scripts..."
BIN="$GEOMOP_INST/bin"
mkdir -p "$BIN"
cat > "$BIN/python" <<EOF
#!/bin/bash
# python wrapper

source /etc/profile

module purge
module load metabase
module add python-3.6.2-gcc python36-modules-gcc

"$GEOMOP_INST/env/bin/python" "\$@"
EOF
chmod +x "$BIN/python"

shift;
executable_list=()
while [[ -n $1 ]]; do
    executable_list+=($1)
    cat > "$BIN/$1" <<EOF
#!/bin/bash
# flow123d wrapper

module purge
module load metabase

"$2" "\$@"
EOF
    chmod +x "$BIN/$1"
    shift;
    shift;
done


echo "Creating installation.json..."
GEOMOP_VER=$(head -n 1 "$CWD/../../VERSION")
GEOMOP_REV=$(git rev-parse HEAD)
cat > "$GEOMOP_INST/installation.json.tmp" << EOF
{
    "executables": [
EOF

for executable in "${executable_list[@]}" ; do
    cat >> "$GEOMOP_INST/installation.json.tmp" << EOF
        {
            "__class__": "Executable",
            "name": "$executable",
            "path": "$GEOMOP_INST/bin/$executable"
        }
        ,
EOF
done

head -n -1 "$GEOMOP_INST/installation.json.tmp" > "$GEOMOP_INST/installation.json"
rm "$GEOMOP_INST/installation.json.tmp"

cat >> "$GEOMOP_INST/installation.json" << EOF
    ],
    "version": "$GEOMOP_VER",
    "revision": "$GEOMOP_REV"
}
EOF
