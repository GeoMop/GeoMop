#!/bin/bash
# Script will install GeoMop on Metacentrum


# get absolute dir in which is this script stored
CWD="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"


function usage {
    echo "Install GeoMop to specified directory."
    echo "Usage: install.sh GEOMOP_ROOT_DIR FLOW123D_PATH"
    exit
}

if [[ $# -ne 2 ]]; then
    usage
    exit
fi


# GeoMop root directory
GEOMOP_INST="$( realpath "$1" )"

# flow123d path
FLOW_PATH="$( realpath "$2" )"


mkdir -p "$GEOMOP_INST"


echo "Creating virtual environment..."
rm -rf "$GEOMOP_INST/env"
module add python-3.4.1-gcc python34-modules-gcc
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
"$GEOMOP_INST/env/bin/pip" install scipy==0.18.1


echo "Copying GeoMop modules..."
SRC="$CWD/../../src"
cp -r "$SRC/common" "$GEOMOP_INST"
cp -r "$SRC/JobPanel" "$GEOMOP_INST"
cp -r "$SRC/Analysis" "$GEOMOP_INST"


echo "Creating scripts..."
BIN="$GEOMOP_INST/bin"
mkdir -p "$BIN"
cat > "$BIN/python" <<EOF
#!/bin/bash
# python wrapper

source /etc/profile

module add python-3.4.1-gcc python34-modules-gcc

"$GEOMOP_INST/env/bin/python" "\$@"
EOF
chmod +x "$BIN/python"

cat > "$BIN/flow123d" <<EOF
#!/bin/bash
# flow123d wrapper

module rm python-3.4.1-gcc python34-modules-gcc

"$FLOW_PATH" "\$@"
EOF
chmod +x "$BIN/flow123d"


echo "Creating executables.json..."
cat > "$GEOMOP_INST/executables.json" <<EOF
[
    {
        "__class__": "Executable",
        "name": "flow123d",
        "path": "$GEOMOP_INST/bin/flow123d"
    }
]
EOF
