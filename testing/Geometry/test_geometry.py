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
import Geometry.geometry as geometry

def check_file(filename):
    file_path = list(os.path.split(filename))
    file_path.insert(-1, 'ref')
    ref_file = os.path.join(*file_path)
    return filecmp.cmp(filename, ref_file)

def run_geometry(in_file, mesh_step=0.0):
    full_in_file = os.path.join('test_data', in_file)
    geometry.make_geometry(layers_file=full_in_file, mesh_step=mesh_step)

    filename_base = os.path.splitext(full_in_file)[0]
    geom_file = filename_base + '.brep'
    assert check_file(geom_file)

    # msh_file = filename_base + '.msh'
    # assert check_file(msh_file)

def test_geometry_script():
     #run_geometry('01_flat_top_side_bc.json')
     #run_geometry('02_bump_top_side_bc.json')
     #run_geometry('03_flat_real_extension.json')
     #run_geometry('04_flat_fracture.json')
     #run_geometry('05_split_square.json', 10)
     #run_geometry('06_bump_split.json', 10)
     run_geometry('10_bump_step.json')
     run_geometry('11_tectonics.json')