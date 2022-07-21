#!/bin/bash

pyuic5 init_dialog.ui -x -o init_dialog_ui.py

cd ../../../gm_base/resources
pyrcc5 geomop_resources.qrc -o geomop_resources.py
