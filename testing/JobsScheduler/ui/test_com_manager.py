import pytest
import os
import shutil

@pytest.fixture
def data():
    import config
    config.__config_dir__ = os.path.join(os.path.split(
            os.path.dirname(os.path.realpath(__file__)))[0], "resources", "mock_settings_cm")

    import ui.data.data_structures as ds
    ds.BASE_DIR = '.'

    return ds.DataContainer()
    
dir = "./data_conf"
    
def make_conf_files(data):
    global dir
    if os.path.isdir(dir):
        clear_conf_files(dir)
    os.mkdir(dir)    
        

def clear_conf_files():
    global dir
    if os.path.isdir(dir):
        shutil.rmtree(dir, ignore_errors=True)
    
def test_local_conn(data, request):
    global dir
    make_conf_files(data)
    
    def fin_test_files():
        clear_conf_files()
    request.addfinalizer(fin_test_files)
    
    assert os.path.isdir(dir)
    
    

