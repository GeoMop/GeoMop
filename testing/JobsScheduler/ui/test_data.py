"""
.. codeauthor:: Tomas Krizek <tomas.krizek1@tul.cz>
"""

import pytest


@pytest.fixture
def data():
    import os
    import config
    config.__config_dir__ = os.path.join(os.path.split(
            os.path.dirname(os.path.realpath(__file__)))[0], "resources", "mock_settings")

    import ui.data.data_structures as ds
    ds.BASE_DIR = '.'

    return ds.DataContainer()


def test_env_preset(data):
    assert len(data.env_presets) == 3

    assert 'hydra' in data.env_presets
    preset = data.env_presets['hydra']
    assert len(preset.cli_params) == 0
    assert preset.flow_path == '/share/apps/flow123d/flow123d-2.0.0_rc/bin/flow123d'
    assert preset.module_add is None
    assert preset.name == 'hydra'
    assert len(preset.pbs_params) == 0
    assert preset.python_exec == '/opt/python/bin/python3.3'
    assert preset.scl_enable_exec is None

    assert 'localhost' in data.env_presets
    preset = data.env_presets['localhost']
    assert len(preset.cli_params) == 0
    assert preset.flow_path == 'C:\\Program Files\\Flow123d 2.0.0_rc\\bin\\flow123d.exe'
    assert preset.module_add is None
    assert preset.name == 'localhost'
    assert len(preset.pbs_params) == 0
    assert preset.python_exec == 'C:\\Program Files (x86)\\GeoMop\\env\\Scripts\\python.exe'
    assert preset.scl_enable_exec is None

    assert 'metacentrum' in data.env_presets
    preset = data.env_presets['metacentrum']
    assert len(preset.cli_params) == 0
    assert preset.flow_path == '/storage/praha1/home/jan-hybs/projects/installed/Flow123d-2.0.0_rc-Linux/bin/flow123d'
    assert preset.module_add == 'python34-modules-gcc'
    assert preset.name == 'metacentrum'
    assert len(preset.pbs_params) == 0
    assert preset.python_exec == 'python'
    assert preset.scl_enable_exec is None


def test_pbs_preset(data):
    assert len(data.pbs_presets) == 2

    assert 'hydra' in data.pbs_presets
    preset = data.pbs_presets['hydra']
    assert preset.infiniband is False
    assert preset.memory is None
    assert preset.name == 'hydra'
    assert preset.nodes == 1
    assert preset.ppn == 1
    assert preset.queue is None
    assert preset.walltime is None

    assert 'metacentrum' in data.pbs_presets
    preset = data.pbs_presets['metacentrum']
    assert preset.infiniband is False
    assert preset.memory is None
    assert preset.name == 'metacentrum'
    assert preset.nodes == 1
    assert preset.ppn == 1
    assert preset.queue == 'q_2h'
    assert preset.walltime is None


def test_resource_preset(data):
    assert len(data.resource_presets) == 3

    assert 'hydra' in data.resource_presets
    preset = data.resource_presets['hydra']
    assert preset.j_env == 'hydra'
    assert preset.j_execution_type == 'REMOTE'
    assert preset.j_pbs_preset == 'hydra'
    assert preset.j_remote_execution_type == 'PBS'
    assert preset.j_ssh_preset == 'hydra'
    assert preset.mj_env == 'hydra'
    assert preset.mj_execution_type == 'DELEGATOR'
    assert preset.mj_pbs_preset == 'hydra'
    assert preset.mj_remote_execution_type == 'PBS'
    assert preset.mj_ssh_preset == 'hydra'
    assert preset.name == 'hydra'

    assert 'local_pc' in data.resource_presets
    preset = data.resource_presets['local_pc']
    assert preset.j_env == 'localhost'
    assert preset.j_execution_type == 'EXEC'
    assert preset.j_pbs_preset is None
    assert preset.j_remote_execution_type is None
    assert preset.j_ssh_preset is None
    assert preset.mj_env == 'localhost'
    assert preset.mj_execution_type == 'EXEC'
    assert preset.mj_pbs_preset is None
    assert preset.mj_remote_execution_type is None
    assert preset.mj_ssh_preset is None
    assert preset.name == 'local_pc'

    assert 'metacentrum' in data.resource_presets
    preset = data.resource_presets['metacentrum']
    assert preset.j_env == 'metacentrum'
    assert preset.j_execution_type == 'PBS'
    assert preset.j_pbs_preset == 'metacentrum'
    assert preset.j_remote_execution_type is None
    assert preset.j_ssh_preset is None
    assert preset.mj_env == 'metacentrum'
    assert preset.mj_execution_type == 'DELEGATOR'
    assert preset.mj_pbs_preset == 'metacentrum'
    assert preset.mj_remote_execution_type == 'PBS'
    assert preset.mj_ssh_preset == 'metacentrum'
    assert preset.name == 'metacentrum'


def test_ssh_preset(data):
    assert len(data.ssh_presets) == 2

    assert 'hydra' in data.ssh_presets
    preset = data.ssh_presets['hydra']
    assert preset.host == 'hydra.kai.tul.cz'
    assert preset.name == 'hydra'
    assert preset.pbs_system == 'pbs_hydra'
    assert preset.port == 22
    assert preset.pwd == 'password'
    assert preset.uid == 'user'

    assert 'metacentrum' in data.ssh_presets
    preset = data.ssh_presets['metacentrum']
    assert preset.host == 'skirit.metacentrum.cz'
    assert preset.name == 'metacentrum'
    assert preset.pbs_system == 'pbs_metacentrum'
    assert preset.port == 22
    assert preset.pwd == 'password'
    assert preset.uid == 'user'
