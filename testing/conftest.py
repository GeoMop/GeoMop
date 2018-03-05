"""
Common test configuration for all test subdirectories.
Put here only those things that can not be done through command line options and pytest.ini file.
"""


import sys
import os
import pytest

print("Root conf test.")
# Modify sys.path to have path to the GeoMop modules.
# TODO: make installation and Tox working in order to remove this hack.
this_source_dir = os.path.dirname(os.path.realpath(__file__))
rel_paths = ["../src"]
for rel_path in rel_paths:
    sys.path.append(os.path.realpath(os.path.join(this_source_dir, rel_path)))
