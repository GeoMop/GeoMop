import pytest
import subprocess
import filecmp
from shutil import copyfile
import sys
import os.path

# def files_cmp(ref,out):
#     with open(ref, "r") as f:
#         t=yml.load(f)
#     with open(ref, "w") as f:
#         yml.dump(t, f)
#     return filecmp.cmp(ref, out)
#
# def remove_prefix(str, prefix):
#     if str.startswith(prefix):
#         return str[len(prefix):]
#     return str


def run_geometry(in_file):
    full_in_file = os.path.join('test_data', in_file)
    subprocess.call(['python3', '../../src/Geometry/geometry.py', full_in_file])



def test_geometry_script():
    #run_geometry('01_flat_top_side_bc.json')
    #run_geometry('02_bump_top_side_bc.json')
    #run_geometry('03_flat_real_extension.json')
    #run_geometry('04_flat_fracture.json')
    run_geometry('05_split_square.json')
    #run_geometry('06_bump_split.json')