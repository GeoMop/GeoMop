import pytest
import subprocess
import filecmp
from shutil import copyfile
import sys
import os.path
import math

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
import LayerEditor.geometry as geometry


def float_line_cmp(l1, l2, tol=1e-6):
    if l1 == l2:
        return True
    s1 = l1.split()
    s2 = l2.split()
    if len(s1) != len(s2):
        return False
    for t1, t2 in zip(s1, s2):
        if t1 == t2:
            continue
        try:
            f1 = float(t1)
            f2 = float(t2)
        except ValueError:
            return False
        if math.fabs(f1 - f2) > tol:
            return False
    return True


def float_file_cmp(f1, f2, tol=1e-6):
    """
    Compare files with float values.
    :param f1: first file name
    :param f2: second file name
    :param tol: tolerance of float values
    :return: True if files are the same
    """
    with open(f1) as fd1:
        with open(f2) as fd2:
            lines1 = fd1.readlines()
            lines2 = fd2.readlines()
            if len(lines1) != len(lines2):
                return False
            for l1, l2 in zip(lines1, lines2):
                if not float_line_cmp(l1, l2, tol):
                    return False
    return True


def check_files(f_geom, f_mesh):
    file_path = list(os.path.split(f_geom))
    file_path.insert(-1, 'ref')
    ref_file = os.path.join(*file_path)
    return float_file_cmp(f_geom, ref_file, 1.0)

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

