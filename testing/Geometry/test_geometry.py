import pytest
import subprocess
import filecmp
from shutil import copyfile
import sys
import os.path

this_source_dir = os.path.dirname(os.path.realpath(__file__))


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

def check_files(f_geom, f_mesh):
    file_path = list(os.path.split(f_geom))
    file_path.insert(-1, 'ref')
    ref_file = os.path.join(*file_path)
    return filecmp.cmp(f_geom, ref_file)

    # For mesh just check that the file exists
    assert os.path.isfile(f_mesh)

@pytest.mark.parametrize("in_file, mesh_step", [
       ('01_flat_top_side_bc.json', 0),
       ('02_bump_top_side_bc.json', 0),
       ('03_flat_real_extension.json', 0),
       ('04_flat_fracture.json', 0),
       ('05_split_square.json', 10),
       ('06_bump_split.json', 10),
       ('10_bump_step.json', 0),
       ('11_tectonics.json', 0)
       ])

def test_run_geometry(in_file, mesh_step):
    full_in_file = os.path.join(this_source_dir, 'test_data', in_file)
    try:
        geometry.make_geometry(layers_file=full_in_file, mesh_step=mesh_step)
    except geometry.ExcGMSHCall as e:
        print(str(e))
        assert False

    filename_base = os.path.splitext(full_in_file)[0]
    geom_file = filename_base + '.brep'
    msh_file = filename_base + '.msh'
    assert check_files(geom_file, msh_file)

