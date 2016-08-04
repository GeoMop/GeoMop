import pytest
import os
import time
import logging

import communicator_files_builder
from ui.com_manager import ComManager
from data.states import TaskStatus
from data.communicator_conf import CommType

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
    
def pause_all(cm, timeout=5):
    # return False for timeout
    cm.pause_all()
    i = 0
    while i<(timeout*10):
        cm.poll()
        if len(cm.start_jobs)==0 and len(cm.run_jobs)==0 and len(cm.delete_jobs)==0:
            return True
        i += 1
        time.sleep(0.1)
    return False

def restore(cm, id, timeout=5):
    # return False for timeout
    cm.resume_jobs.append(id)
    i = 0
    while i<(timeout*10):
        cm.poll()
        if len(cm.resume_jobs)==0:
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
    
def terminate(cm, id, timeout=5):
    # return False for timeout
    cm.terminate_jobs.append(id)
    i = 0
    while i<(timeout*10):
        cm.poll()
        if  len(cm.start_jobs)==0 and len(cm.run_jobs)==0 and len(cm.delete_jobs)==0 :
            return True
        i += 1
        time.sleep(0.1)
    return False

def delete(cm, id, timeout=5):
    # return False for timeout
    cm.delete_jobs.append(id)
    i = 0
    while i<(timeout*10):
        cm.poll()
        if  len(cm.start_jobs)==0 and len(cm.run_jobs)==0 and len(cm.delete_jobs)==0 :
            return True
        i += 1
        time.sleep(0.1)
    return False

def get_communicator(cm, key):
    if key in cm._workers:
        worker = cm._workers[key]
        return worker._com
    return None

def reset_app_handler():
    logger = logging.getLogger("Remote")
    for hdlr in logger.handlers:
        logger.removeHandler(hdlr)
   
def test_local(request, data):
    run_mj = []
    cm = ComManager(data) 
    def fin_test_local():        
        for mj in run_mj:
            stop(cm, mj)   
        # communicator_files_builder.clear_files(TEST_DIR)
    request.addfinalizer(fin_test_local)
    mj = data.multijobs["test2_local_2"]
    # test start - stop, start - terminate
    for action in ["stop", "terminate"]:
        communicator_files_builder.make_installation(TEST_DIR, data)            
        assert start(cm, 'test2_local_2')   
        if mj.state.status == TaskStatus.error:
            assert False, "Can't start multijob({0})".format(mj.error) 
        run_mj = ['test2_local_2']
        assert mj.state.status != TaskStatus.finished
        assert len(cm.run_jobs)==1
        if action == "stop":
            assert stop(cm, 'test2_local_2')
        else:
            assert terminate(cm, 'test2_local_2')
        run_mj = []

        assert len(cm.run_jobs)==0
        assert len(cm.delete_jobs)==0

        com = get_communicator(cm,"test2_local_2")
        if com is not None and com.is_running_next():
            com.kill_next()
            assert False, "Next communicator still run !!!"

        mj_name = data.multijobs["test2_local_2"].preset.name    
        an_name = data.multijobs["test2_local_2"].preset.analysis
        app_log = communicator_files_builder.get_central_log() 
        assert app_log.records > 0
        mj_log = communicator_files_builder.get_log(an_name, mj_name, CommType.multijob)
        assert mj_log.records > 0
        assert app_log.infos[0] == "Application app is started"
        assert app_log.infos[-1] == "Connection to application app is stopped"
        assert len(app_log.errors) == 0
        assert  mj_log.infos[0] == "Application mj_service is started"
        if action == "stop":
            assert  mj_log.infos[-2] == "Connection to application mj_service is stopped"
            assert  mj_log.infos[-1] == "Application mj_service is stopped"
            assert len( mj_log.errors) == 0  
        else:
            assert  mj_log.errors[0] == "Communicator was destroyed"

        communicator_files_builder.clear_files(TEST_DIR)
        reset_app_handler()
    
    """
    # start / pause / resume /  stop / delete 
    assert start(cm, 'test2_local_2')   
    if mj.state.status == TaskStatus.error:
        assert False, "Can't start multijob({0})".format(mj.error) 
    run_mj = ['test2_local_2']
    assert mj.state.status != TaskStatus.finished
    assert len(cm.run_jobs)==1
    
    assert pause_all(cm, 'test2_local_2')
    
    assert restore(cm, 'test2_local_2')   
    
    assert stop(cm, 'test2_local_2')
 

    run_mj = []
   
    assert len(cm.run_jobs)==0
    assert len(cm.delete_jobs)==0
 
    com = get_communicator(cm,"test2_local_2")
    if com is not None and com.is_running_next():
        com.kill_next()
        assert False, "Next communicator still run !!!"
    
    mj_name = data.multijobs["test2_local_2"].preset.name    
    an_name = data.multijobs["test2_local_2"].preset.analysis
    app_log = communicator_files_builder.get_central_log() 
    assert app_log.records > 0
    mj_log = communicator_files_builder.get_log(an_name, mj_name, CommType.multijob)
    assert mj_log.records > 0
    assert app_log.infos[0] == "Application app is started"
    assert app_log.infos[-1] == "Connection to application app is stopped"
    assert len(app_log.errors) == 0
    assert  mj_log.infos[0] == "Application mj_service is started"
    assert  mj_log.infos[-2] == "Connection to application mj_service is stopped"
    assert  mj_log.infos[-1] == "Application mj_service is stopped"
    assert len( mj_log.errors) == 0          
    """


