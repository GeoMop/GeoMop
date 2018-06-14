"""
.. codeauthor:: Tomas Krizek <tomas.krizek1@tul.cz>
"""
import pytest
import os

from gm_base.model_data import (export_con, Loader)

__model_data_dir__ =  os.path.dirname(os.path.realpath(__file__))
DATA_DIR = os.path.join(__model_data_dir__, 'export_con')


@pytest.fixture(scope='module')
def loader():
    return Loader()


@pytest.mark.parametrize('filename', [
    'boolean',
    'integer',
    'double',
    'scalar',
    'mapping',
    'sequence',
    'abstract_record',
    'reference',
    'dual_por_pade'
])
def test_export_con_bool(filename, loader):
    yaml_file = os.path.join(DATA_DIR, filename + '.yaml')
    con_file = os.path.join(DATA_DIR, filename + '.con')

    with open(yaml_file) as file:
        yaml = file.read()

    root = loader.load(yaml)
    text = export_con(root)

    with open(con_file) as file:
        con = file.read()

    assert con == text
