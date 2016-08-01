import pytest
import os
import time

import communicator_files_builder
from ui.com_manager import ComManager
from data.states import TaskStatus

HOME_DIR = os.path.split(os.path.dirname(os.path.realpath(__file__)))[0]
TEST_DIR = os.path.join(HOME_DIR, "test")
LOCAL_FLOW_DIR = "/opt/flow/Flow123d-2.0.0_rc-Linux/bin/flow123d"
SETTINGS_DIR =  os.path.join(HOME_DIR, "resources", "mock_settings_cm")

@pytest.fixture
def data():    
    import config
    config.__config_dir__ = SETTINGS_DIR

    import ui.data.data_structures as ds
    ds.BASE_DIR = '.'

    return ds.DataContainer()
    
def start(cm, id, timeout=5):
    # return False for timeout
    cm.start_jobs.append(id)
    i = 0
    while i<(timeout*10):
        cm.poll()
        if len(cm.start_jobs)==0:
            return True
        i += 1
        time.sleep(0.1)
    return False
    
def stop(cm, id, timeout=5):
    # return False for timeout
    cm.stop_jobs.append(id)
    i = 0
    while i<(timeout*10):
        cm.poll()
        if  len(cm.start_jobs)==0 and len(cm.run_jobs)==0 and len(cm.delete_jobs)==0 :
            return True
        i += 1
        time.sleep(0.1)
    return False
    
def test_local(request, data):
    def fin_test_local():
        communicator_files_builder.clear_files(TEST_DIR)
    request.addfinalizer(fin_test_local)
    mj = data.multijobs["test2_local_2"]
    communicator_files_builder.make_installation(TEST_DIR, data)      
    cm = ComManager(data)    
    # test start - stop
    assert start(cm, 'test2_local_2')
    if mj.state.status == TaskStatus.error:
        assert False, "Can't start multijob({0})".format(mj.error) 
    assert mj.state.status != TaskStatus.finished
    assert len(cm.run_jobs)==1    
    assert stop(cm, 'test2_local_2')
    assert len(cm.run_jobs)==0
    assert len(cm.delete_jobs)==0   
    
    

