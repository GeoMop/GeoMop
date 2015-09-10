import config
import os

class DataForTest:
    def __init__(self):
        self.inner = DataForTestInner()
        self.name = "ooo"
        
    
class DataForTestInner:
    def __init__(self):
        self.a = 0 
        self.b = 1

def test_config_save_and_load():
    #config dir exist
    assert os.path.isdir(config.__config_dir__)
    data = DataForTest()
    data.inner.a = 6
    data.name="test1"
    config.save_config_file("test_data", data)
    data.inner.a = 7
    data.name="test2"
    data = config.get_config_file("test_data")
    assert data.inner.a ==6
    assert data.name == "test1"
    data.inner.a = 7
    data.name="test2"
    config.save_config_file("test_data", data)
    data = config.get_config_file("test_data")
    assert data.inner.a ==7
    assert data.name == "test2"
    config.delete_config_file("test_data")
    data = config.get_config_file("test_data")
    assert data == None
    config.delete_config_file("test_data")
    
    
