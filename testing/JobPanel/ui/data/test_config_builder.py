import pytest
import os

import testing.JobPanel.mock.communicator_files_builder as communicator_files_builder
from JobPanel.ui.data.config_builder import ConfBuilder
from JobPanel.data.communicator_conf import CommType

HOME_DIR = os.path.split(os.path.split(os.path.dirname(os.path.realpath(__file__)))[0])[0]
TEST_DIR = os.path.join(HOME_DIR, "test")
FLOW_DIR = "/opt/flow/Flow123d-2.0.0_rc-Linux/bin/flow123d"
SETTINGS_DIR =  os.path.join(HOME_DIR, "resources", "mock_settings_cm")

@pytest.fixture
def data():    
    import config
    config.__config_dir__ = SETTINGS_DIR

    import JobPanel.ui.imports.workspaces_conf as wc
    wc.BASE_DIR = '.'
    import JobPanel.ui.data.data_structures as ds
    
    container = ds.DataContainer()
    container.config.local_env = 'local'
    
    return container
    
def test_conf_builder(request, data):
    def fin_test_dir_create():
        communicator_files_builder.clear_files(TEST_DIR)
    request.addfinalizer(fin_test_dir_create)
    
    assert len(data.multijobs) == 2
    assert "test2_local_2" in data.multijobs
    
    builder = communicator_files_builder.make_builder(TEST_DIR, data)  
    builder.mj_name = data.multijobs["test2_local_2"].preset.name
    builder.an_name = data.multijobs["test2_local_2"].preset.analysis
    
    app = ConfBuilder(builder)
    app.set_comm_name(CommType.app)
    assert app.get_path()[:len(TEST_DIR)] == TEST_DIR

def test_builder_create(request, data):
    def fin_test_dir_create():
        communicator_files_builder.clear_files(TEST_DIR)
    request.addfinalizer(fin_test_dir_create)
    
    assert len(data.multijobs) == 2
    assert "test2_local_2" in data.multijobs
    builder = communicator_files_builder.make_builder(TEST_DIR, data)
    assert len(data.multijobs) == len(builder.multijobs)
    assert "test2_local_2" in builder.multijobs
    
    app = builder.build("test2_local_2")
    assert app.an_name == "test2"
    assert app.central_log
    assert len(app.cli_params) == 0
    assert app.communicator_name == "app"
    assert not app.direct_communication
    assert app.flow_path is None
    assert app.input_type == 0
    assert not app.libs_env.install_job_libs
    assert app.mj_name == "local_2"
    assert app.next_communicator == "mj_service"
    assert app.number_of_processes == 1
    assert app.output_type == 2
    assert app.paths_config.app_dir is None
    assert app.paths_config.home_dir[:len(TEST_DIR)] == TEST_DIR
    assert app.paths_config.work_dir[:len(TEST_DIR)] == TEST_DIR
    assert app.pbs is None
    assert app.port == 5723
    assert app.python_env.python_exec == "python3"
    assert app.ssh is None
    
def test_dir_create(request, data):
    def fin_test_dir_create():
        communicator_files_builder.clear_files(TEST_DIR)
    request.addfinalizer(fin_test_dir_create)
    
    assert len(data.multijobs) == 2
    assert "test2_local_2" in data.multijobs
    communicator_files_builder.make_work_dir(TEST_DIR, data, 'test2_local_2')
    
    mj_name = data.multijobs["test2_local_2"].preset.name
    an_name = data.multijobs["test2_local_2"].preset.analysis
    mj_conf = communicator_files_builder.get_config(an_name, mj_name, CommType.multijob)
    
    assert mj_conf.an_name == "test2"
    assert not mj_conf.central_log
    assert len(mj_conf.cli_params) == 0
    assert mj_conf.communicator_name == "mj_service"
    assert not mj_conf.direct_communication
    assert mj_conf.flow_path == FLOW_DIR
    assert mj_conf.input_type == 2
    assert not mj_conf.libs_env.install_job_libs
    assert mj_conf.mj_name == "local_2"
    assert mj_conf.next_communicator == "job"
    assert mj_conf.number_of_processes == 1
    assert mj_conf.output_type == 2
    assert mj_conf.paths_config.app_dir is None
    assert mj_conf.paths_config.home_dir[:len(TEST_DIR)] == TEST_DIR
    assert mj_conf.paths_config.work_dir[:len(TEST_DIR)] == TEST_DIR
    assert mj_conf.pbs is None
    assert mj_conf.port == 5723
    assert mj_conf.python_env.python_exec == "python3"
    assert mj_conf.ssh is None
    
    job_conf = communicator_files_builder.get_config(an_name, mj_name, CommType.job)

    assert job_conf.an_name == "test2"
    assert not job_conf.central_log
    assert len(job_conf.cli_params) == 0
    assert job_conf.communicator_name == "job"
    assert not job_conf.direct_communication
    assert job_conf.flow_path == FLOW_DIR
    assert job_conf.input_type == 2
    assert not job_conf.libs_env.install_job_libs
    assert job_conf.mj_name == "local_2"
    assert job_conf.next_communicator == ""
    assert job_conf.number_of_processes == 1
    assert job_conf.output_type == 0
    assert job_conf.paths_config.app_dir is None
    assert job_conf.paths_config.home_dir[:len(TEST_DIR)] == TEST_DIR
    assert job_conf.paths_config.work_dir[:len(TEST_DIR)] == TEST_DIR
    assert job_conf.pbs is None
    assert job_conf.port == 5723
    assert job_conf.python_env.python_exec == "python3"
    assert job_conf.ssh is None
