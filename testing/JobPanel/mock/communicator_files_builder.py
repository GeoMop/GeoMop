import shutil
import os
import config
import logging

from JobPanel.ui.data.config_builder import ConfigBuilder
from JobPanel.communication import Installation
import JobPanel.data.communicator_conf as comconf
from .log_reader import Log
from JobPanel.data import Users

__HOME__ = "home"
__WORKSPACE__ = "workspace"

def make_work_dir(dir, data,  key):
    make_installation(dir, data)
    conf_builder = ConfigBuilder(data)
    app_conf = conf_builder.build(key)
    return app_conf

def make_builder(dir, data):
    make_installation(dir, data)
    conf_builder = ConfigBuilder(data)
    return conf_builder

def get_config(an_name, mj_name, com_type):
    path = Installation.get_config_dir_static(mj_name, an_name)
    path = os.path.join(path, com_type.value + ".json")
    com_conf = comconf.CommunicatorConfig()
    with open(path, "r") as json_file:
        comconf.CommunicatorConfigService.load_file(json_file, com_conf)
    return com_conf
    
def get_log(an_name, mj_name, com_type, id=None):
    path = Installation. get_mj_log_dir_static(mj_name, an_name)
    if id is None:
        path = os.path.join(path, com_type.value + ".log")    
    else:
        path = os.path.join(path, com_type.value + "_" + id + ".log")    
    log = Log(path)
    return log

def get_central_log(): 
    path = Installation. get_central_log_dir_static()
    path = os.path.join(path, "app-centrall.log")
    log = Log(path)
    return log

def make_installation(dir, data):
    home = os.path.join( dir, __HOME__)
    reg_dir = os.path.join( dir, __HOME__, "JobPanel")
    workspace = os.path.join( dir, __WORKSPACE__) 
    if os.path.isdir(dir):
        clear_files(dir)
    if not os.path.isdir(dir):
        os.makedirs(dir)
    if not os.path.isdir(home):
        os.makedirs(home)
    if not os.path.isdir(reg_dir):
        os.makedirs(reg_dir)
    if not os.path.isdir(workspace):
        os.makedirs(workspace)
    Installation.set_init_paths(home, workspace)
    assert len(data.workspaces.workspaces) == 1
    data.workspaces.workspaces[data.workspaces.selected].path = workspace
    config.__config_dir__ = home
    for ssh in data.ssh_presets:        
        if data.ssh_presets[ssh].to_pc:
            data.ssh_presets[ssh].key = Users.save_reg(data.ssh_presets[ssh].name,data.ssh_presets[ssh].pwd, reg_dir)
    
def clear_files(dir):
    shutil.rmtree(dir, ignore_errors=True)
    # remove centrall app logger handler
    logger = logging.getLogger("Remote")
    for hdlr in logger.handlers:
        logger.removeHandler(hdlr)
    
def copy_an_to_config(an_name, mj_name, an_dir):
    path = Installation. get_input_dir_static(mj_name, an_name)
    names = os.listdir(an_dir)    
    for name in names:
        src = os.path.join(an_dir, name)
        if os.path.isdir(src):            
            dst = os.path.join(path, name)
            if os.path.isdir(dst):
                shutil.rmtree(dst, ignore_errors=True)
            shutil.copytree(src, dst)
        else:
            shutil.copy(src, path)
