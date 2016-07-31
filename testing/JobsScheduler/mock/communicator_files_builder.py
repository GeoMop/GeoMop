import shutil
import os

from ui.data.config_builder import ConfigBuilder
from communication import Installation
import data.communicator_conf as comconf

__HOME__ = "home"
__WORKSPACE__ = "workspace"

def make_work_dir(dir, data,  key):
    make_installation(dir)
    conf_builder = ConfigBuilder(data)
    app_conf = conf_builder.build(key)
    return app_conf

def make_builder(dir, data):
    make_installation(dir)
    conf_builder = ConfigBuilder(data)
    return conf_builder

def get_config(dir, an_name, mj_name, com_type):
    path = Installation.get_config_dir_static(mj_name, an_name)
    path = os.path.join(path, com_type.value + ".json")
    com_conf = comconf.CommunicatorConfig()
    with open(path, "r") as json_file:
        comconf.CommunicatorConfigService.load_file(json_file, com_conf)
    return com_conf

def make_installation(dir):
    home = os.path.join( dir, __HOME__)
    workspace = os.path.join( dir, __WORKSPACE__) 
    if os.path.isdir(dir):
        clear_files(dir)
    if not os.path.isdir(dir):
        os.makedirs(dir)
    if not os.path.isdir(home):
        os.makedirs(home)
    if not os.path.isdir(workspace):
        os.makedirs(workspace)
    Installation.set_init_paths(home, workspace)    
    
def clear_files(dir):
    shutil.rmtree(dir, ignore_errors=True)
