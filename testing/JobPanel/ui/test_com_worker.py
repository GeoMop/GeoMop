import pytest
import os
import time

import testing.JobPanel.mock.communicator_files_builder as communicator_files_builder
import sys
if sys.platform == "win32":
    import testing.JobPanel.mock.ssh_helper_win as ssh_helper
else:
    import testing.JobPanel.mock.ssh_helper_linux as ssh_helper
from JobPanel.ui.data.config_builder import ConfigBuilder
from JobPanel.communication import Communicator
from JobPanel.ui.com_worker import ComWorker

HOME_DIR = os.path.split(os.path.dirname(os.path.realpath(__file__)))[0]
TEST_DIR = os.path.join(HOME_DIR, "test")
LOCAL_FLOW_DIR = "/opt/flow/Flow123d-2.0.0_rc-Linux/bin/flow123d"
SETTINGS_DIR =  os.path.join(HOME_DIR, "resources", "mock_settings_cm")
ANAL_DIR =  os.path.join(HOME_DIR, "resources", "mock_an_cm")

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
    
def start(data, key, timeout=5):
    conf_builder = ConfigBuilder(data)
    app_conf = conf_builder.build(key)
    ConfigBuilder.gain_login(app_conf)                
    com = Communicator(app_conf)
    worker = ComWorker(key, com)
    worker.start_mj()
    i = 0
    while i<(timeout*10):
        assert not worker.is_error()
        if worker.is_started():
            return worker        
        i += 1
        time.sleep(0.1)
    return None                
    
def stop(worker, timeout=5):
    # return False for timeout
    assert not worker.is_cancelling()                   
    worker.stop()
    i = 0
    while i<(timeout*10):
        assert not worker.is_error()
        if worker.is_cancelled():
            return True 
        i += 1
        time.sleep(0.1)
    return None                
    
def test_local(request, data):
    mj_name = data.multijobs["test2_local_ssh"].preset.name    
    an_name = data.multijobs["test2_local_ssh"].preset.analysis
    
    communicator_files_builder.make_installation(TEST_DIR, data)
    communicator_files_builder.copy_an_to_config(an_name, mj_name, ANAL_DIR)
    
    worker = start(data, "test2_local_2")
    assert worker is not None
    def fin_test_local():        
        if worker is not None:            
            stop(worker)
        # communicator_files_builder.clear_files(TEST_DIR)
    request.addfinalizer(fin_test_local)
    assert stop(worker)
    
def test_ssh(request, data):
    mj_name = data.multijobs["test2_local_ssh"].preset.name    
    an_name = data.multijobs["test2_local_ssh"].preset.analysis
    
    communicator_files_builder.make_installation(TEST_DIR, data)
    communicator_files_builder.copy_an_to_config(an_name, mj_name, ANAL_DIR)

    ssh_helper.check_pexpect(data, "test2_local_ssh")
    ssh_helper.clear_ssh_installation(data, "test2_local_ssh")
    
    worker = start(data, "test2_local_ssh", 100)
    assert worker is not None
    def fin_test_local():        
        if worker is not None:            
            stop(worker)
        ssh_helper.clear_ssh_installation(data, "test2_local_ssh")
        communicator_files_builder.clear_files(TEST_DIR)
       
    request.addfinalizer(fin_test_local)
    assert stop(worker, 60)
    
