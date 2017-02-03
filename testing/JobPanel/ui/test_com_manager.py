import pytest
import os
import time

import communicator_files_builder
import sys
if sys.platform == "win32":
    import ssh_helper_win as ssh_helper
else:
    import ssh_helper_linux as ssh_helper
from ui.com_manager import ComManager
from data.states import TaskStatus
from data.communicator_conf import CommType

HOME_DIR = os.path.split(os.path.dirname(os.path.realpath(__file__)))[0]
TEST_DIR = os.path.join(HOME_DIR, "test")
LOCAL_FLOW_DIR = "/opt/flow/Flow123d-2.0.0_rc-Linux/bin/flow123d"
SETTINGS_DIR =  os.path.join(HOME_DIR, "resources", "mock_settings_cm")
ANAL_DIR =  os.path.join(HOME_DIR, "resources", "mock_an_cm")

@pytest.fixture
def data():    
    import config
    config.__config_dir__ = SETTINGS_DIR

    import ui.imports.workspaces_conf as wc
    wc.BASE_DIR = '.'
    import ui.data.data_structures as ds

    container = ds.DataContainer()
    container.config.local_env = 'local'
    return container
    
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
    return wait_to_end(cm, id, timeout)
    
def wait_to_end(cm, id, timeout=5):
    i = 0
    while i<(timeout*10):
        cm.poll()
        if  len(cm.start_jobs)==0 and len(cm.run_jobs)==0 and len(cm.delete_jobs)==0 :
            time.sleep(1)
            return True
        i += 1
        time.sleep(0.1)
    return False
    
def terminate(cm, id, timeout=5):
    # return False for timeout
    cm.terminate_jobs.append(id)
    return wait_to_end(cm, id, timeout)

def delete(cm, id, timeout=5):
    # return False for timeout
    cm.delete_jobs.append(id)
    return wait_to_end(cm, id, timeout)
    
def wait_to_finish(cm, id, timeout=25):
    # return False for timeout
    i = 0
    mj = cm._data_app.multijobs[id]                   
    while i<(timeout*10):
        cm.poll()
        if len(cm.state_change_jobs)>0:
            cm.state_change_jobs = []
            if mj.get_state().get_status() == TaskStatus.finished or \
                mj.get_state().get_status() == TaskStatus.error:
                return wait_to_end(cm, id)
        time.sleep(0.1)
        i += 1
    assert mj.get_state().get_status() == TaskStatus.finished or \
        mj.get_state().get_status() == TaskStatus.error   
    return False
    
def get_communicator(cm, key):
    if key in cm._workers:
        worker = cm._workers[key]
        return worker._com
    return None
    
def kill_next_communicator(cm, key):
    if key in cm._workers:
        worker = cm._workers[key]
        worker._com.kill_next()
  
def test_local(request, data):
    run_mj = []
    pause_mj = []
    cm = ComManager(data) 
    def fin_test_local():        
        for mj in run_mj:
            stop(cm, mj)
        for mj in pause_mj:
            restore(cm, mj) 
            stop(cm, mj)
        communicator_files_builder.clear_files(TEST_DIR)
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
        assert len(cm.start_jobs)==0

        com = get_communicator(cm,"test2_local_2")
        if com is not None and com.is_running_next():
            com.kill_next()
            assert False, "Next communicator still run !!!"
        assert com is None, "Next communicator still set !!!"

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
    
    # start / pause / resume /  stop / delete
    communicator_files_builder.make_installation(TEST_DIR, data)  
    assert start(cm, 'test2_local_2') 
    if mj.state.status == TaskStatus.error:
        assert False, "Can't start multijob({0})".format(mj.error) 
    run_mj = ['test2_local_2']
    assert mj.state.status != TaskStatus.finished
    assert len(cm.run_jobs)==1
    assert pause_all(cm)
    
    pause_mj = ['test2_local_2']
    run_mj = []    
        
    if com is not None and com.is_running_next():            
        assert False, "Next communicator still run !!!"
    assert com is None, "Next communicator still set !!!"

    assert len(cm.run_jobs)==0
    assert len(cm.delete_jobs)==0
    assert len(cm.start_jobs)==0
    
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
    assert  mj_log.infos[-1] == "Application mj_service is interupted"
    assert len( mj_log.errors) == 0 
    
    time.sleep(12)
    assert restore(cm, 'test2_local_2') 
    pause_mj = []
    run_mj = ['test2_local_2']
    assert mj.state.status != TaskStatus.finished
    assert len(cm.run_jobs)==1  
    assert stop(cm, 'test2_local_2')

    run_mj = []   
    assert len(cm.run_jobs)==0    
    assert len(cm.delete_jobs)==0
 
    com = get_communicator(cm,"test2_local_2")
    if com is not None and com.is_running_next():
        com.kill_next()
        assert False, "Next communicator still run !!!"
    
    app_log = communicator_files_builder.get_central_log() 
    assert app_log.records > 0
    mj_log = communicator_files_builder.get_log(an_name, mj_name, CommType.multijob)
    assert mj_log.records > 0    
    assert app_log.infos[-1] == "Connection to application app is stopped"
    assert app_log.infos[-2] == "Application app is restored"
    assert len(app_log.errors) == 0
    assert  mj_log.infos[-4] == "Application mj_service is restored"
    assert  mj_log.infos[-3] == "Stop signal is received"
    assert  mj_log.infos[-2] == "Connection to application mj_service is stopped"
    assert  mj_log.infos[-1] == "Application mj_service is stopped"
    assert len( mj_log.errors) == 0

    assert delete(cm, 'test2_local_2')
    
    app_log = communicator_files_builder.get_central_log() 
    assert app_log.records > 0
    mj_log = communicator_files_builder.get_log(an_name, mj_name, CommType.multijob)
    assert mj_log.records > 0    
    assert app_log.infos[-1] == "Connection to application app is stopped"
    assert app_log.infos[-2] == "Application app is restored"
    assert len(app_log.errors) == 0
    assert  mj_log.infos[-4] == "Application mj_service is restored"
    assert  mj_log.infos[-3] == "Delete signal is received"
    assert  mj_log.infos[-2] == "Connection to application mj_service is stopped"
    assert  mj_log.infos[-1] == "Application mj_service is stopped"
    assert len( mj_log.errors) == 0
    
    communicator_files_builder.clear_files(TEST_DIR)

def test_local_with_data(request, data):
    run_mj = []
    cm = ComManager(data) 
    def fin_test_local():        
        for mj in run_mj:
            stop(cm, mj)
        communicator_files_builder.clear_files(TEST_DIR)
    request.addfinalizer(fin_test_local)
    mj = data.multijobs["test2_local_2"]
    
    mj_name = data.multijobs["test2_local_2"].preset.name    
    an_name = data.multijobs["test2_local_2"].preset.analysis
    
    communicator_files_builder.make_installation(TEST_DIR, data)
    communicator_files_builder.copy_an_to_config(an_name, mj_name, ANAL_DIR)

    assert start(cm, 'test2_local_2')  
    run_mj = ['test2_local_2']
    assert wait_to_finish(cm, 'test2_local_2') 
    run_mj = []
    if mj.state.status == TaskStatus.error:
        assert False, "Can't start multijob({0})".format(mj.error) 
    assert mj.state.status == TaskStatus.finished    

    assert len(cm.run_jobs)==0
    assert len(cm.delete_jobs)==0
    assert len(cm.start_jobs)==0

    com = get_communicator(cm,"test2_local_2")
    if com is not None and com.is_running_next():
        com.kill_next()
        assert False, "Next communicator still run !!!"
    assert com is None, "Next communicator still set !!!"
    
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

    communicator_files_builder.clear_files(TEST_DIR)

def test_ssh(request, data):
    run_mj = []
    pause_mj = []
    cm = ComManager(data) 
    instalation = None
    def fin_test_local():
        for mj in run_mj:
            stop(cm, mj)
        for mj in pause_mj:
            restore(cm, mj) 
            stop(cm, mj)       
        if instalation is not None:
            ssh_helper.clear_ssh_installation(data, instalation)        
        communicator_files_builder.clear_files(TEST_DIR)
    request.addfinalizer(fin_test_local)   
    
    mj_name = data.multijobs["test2_local_ssh"].preset.name    
    an_name = data.multijobs["test2_local_ssh"].preset.analysis    
   
    communicator_files_builder.make_installation(TEST_DIR, data)
    communicator_files_builder.copy_an_to_config(an_name, mj_name, ANAL_DIR)

    ssh_helper.check_pexpect(data, "test2_local_ssh")
    ssh_helper.clear_ssh_installation(data, "test2_local_ssh")
    mj = data.multijobs["test2_local_ssh"]
    
    assert start(cm, 'test2_local_ssh', 100)
    instalation =  'test2_local_ssh'
    assert wait_to_finish(cm, 'test2_local_ssh') 
    if mj.state.status == TaskStatus.error:
        assert False, "Can't start multijob({0})".format(mj.error) 
    run_mj = ['test2_local_ssh']
    run_mj = []

    assert len(cm.run_jobs)==0
    assert len(cm.delete_jobs)==0
    assert len(cm.start_jobs)==0

    com = get_communicator(cm,"test2_local_ssh")
    if com is not None and com.is_running_next():
        com.kill_next()
        assert False, "Next communicator still run !!!"
    assert com is None, "Next communicator still set !!!"
    
    app_log = communicator_files_builder.get_central_log() 
    assert app_log.records > 0
    mj_log = communicator_files_builder.get_log(an_name, mj_name, CommType.multijob)
    assert mj_log.records > 0
    job1_log = communicator_files_builder.get_log(an_name, mj_name, CommType.job, "flow1")
    assert job1_log.records > 0
    delegator_log = communicator_files_builder.get_log(an_name, mj_name, CommType.delegator)
    assert delegator_log.records > 0

    assert app_log.infos[0] == "Application app is started"
    assert app_log.infos[-1] == "Connection to application app is stopped"
    assert len(app_log.errors) == 0
    assert  mj_log.infos[0] == "Application mj_service is started"
    assert len( mj_log.errors) == 0
    assert  job1_log.infos[0] == "Application job is started"
    assert job1_log.infos[-1] == "End"
    assert job1_log.infos[-2] == "Connection to application job is stopped"
    assert  delegator_log.infos[0] == "Application delegator is started"
    assert len( mj_log.errors) == 0
    
    ssh_helper.check_ssh_installation(data, "test2_local_ssh")
    
    communicator_files_builder.clear_files(TEST_DIR)
    communicator_files_builder.make_installation(TEST_DIR, data)
    communicator_files_builder.copy_an_to_config(an_name, mj_name, ANAL_DIR)  

    assert start(cm, 'test2_local_ssh', 100)  
    if mj.state.status == TaskStatus.error:
        assert False, "Can't start multijob({0})".format(mj.error) 
    run_mj = ['test2_local_ssh']
    assert mj.state.status != TaskStatus.finished
    assert len(cm.run_jobs)==1
    assert pause_all(cm, 60)
    
    pause_mj = ['test2_local_ssh']
    run_mj = []    
        
    if com is not None and com.is_running_next():            
        assert False, "Next communicator still run !!!"
    assert com is None, "Next communicator still set !!!"

    assert len(cm.run_jobs)==0
    assert len(cm.delete_jobs)==0
    assert len(cm.start_jobs)==0
    
    app_log = communicator_files_builder.get_central_log() 
    assert app_log.records > 0
    assert app_log.infos[0] == "Application app is started"
    assert app_log.infos[-1] == "Connection to application app is stopped"
    
    time.sleep(12)
    assert restore(cm, 'test2_local_ssh', 60) 
    pause_mj = []
    run_mj = ['test2_local_ssh']
    assert mj.state.status != TaskStatus.finished
    assert len(cm.run_jobs)==1  
    
    assert wait_to_finish(cm, 'test2_local_ssh') 
    if mj.state.status == TaskStatus.error:
        assert False, "Can't start multijob({0})".format(mj.error) 
    run_mj = ['test2_local_ssh']
    run_mj = []

    assert len(cm.run_jobs)==0
    assert len(cm.delete_jobs)==0
    assert len(cm.start_jobs)==0

    com = get_communicator(cm,"test2_local_ssh")
    if com is not None and com.is_running_next():
        com.kill_next()
        assert False, "Next communicator still run !!!"
    assert com is None, "Next communicator still set !!!"
    
    app_log = communicator_files_builder.get_central_log() 
    assert app_log.records > 0
    mj_log = communicator_files_builder.get_log(an_name, mj_name, CommType.multijob)
    assert mj_log.records > 0
    job1_log = communicator_files_builder.get_log(an_name, mj_name, CommType.job, "flow1")
    assert job1_log.records > 0
    delegator_log = communicator_files_builder.get_log(an_name, mj_name, CommType.delegator)
    assert delegator_log.records > 0

    assert app_log.infos[0] == "Application app is started"
    assert app_log.infos[-1] == "Connection to application app is stopped"
    assert len(app_log.errors) == 0
    assert  mj_log.infos[0] == "Application mj_service is started"
    assert len( mj_log.errors) == 0
    assert  job1_log.infos[0] == "Application job is started"
    assert job1_log.infos[-1] == "End"
    assert job1_log.infos[-2] == "Connection to application job is stopped"
    assert  delegator_log.infos[0] == "Application delegator is started"
    assert len( mj_log.errors) == 0
    
    ssh_helper.clear_ssh_installation(data, "test2_local_ssh")
    communicator_files_builder.clear_files(TEST_DIR)
    instalation = None
