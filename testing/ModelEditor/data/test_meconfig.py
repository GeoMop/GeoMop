from data.meconfig import MEConfig as cfg
from data.meconfig import _Config as Config

def test_config(request):
    Config.SERIAL_FILE = "ModelEditorData_test"
    cfg.init(None)
    cfg.config = Config()
    # cfg.config is assigned
    assert cfg.config.__class__ == Config
    
    def fin_test_config():
        import config
        config.delete_config_file("ModelEditorData_test")
    request.addfinalizer(fin_test_config)    
    
    from os.path import expanduser
    home = expanduser("~")
    # last_data_dir for first opened config is home
    assert home == cfg.config.last_data_dir
    config = Config(False)
    # new config have last_data_dir == home
    assert home == config.last_data_dir
    
    cfg.config.add_recent_file("test_file1", "test_format_file1")
    # add first file
    assert cfg.config.recent_files[0] == "test_file1"
    assert cfg.config.format_files[0] == "test_format_file1"
    
    cfg.config.add_recent_file("test_file1", "test_format_file_new_1")
    # change only format
    assert cfg.config.format_files[0] == "test_format_file_new_1"
    assert len(cfg.config.format_files) == 1
    
    cfg.config.add_recent_file("test_file2", "test_format_file2")
    cfg.config.add_recent_file("test_file3", "test_format_file3")
    # add 3 files
    assert len(cfg.config.format_files) == 3
    assert cfg.config.recent_files[0] == "test_file3"
    assert cfg.config.format_files[0] == "test_format_file3"
    assert cfg.config.recent_files[2] == "test_file1"
    assert cfg.config.format_files[2] == "test_format_file_new_1"
    
    cfg.config.add_recent_file("test_file2", "test_format_file2")
    # move 2 to first line
    assert len(cfg.config.format_files) == 3
    assert cfg.config.recent_files[0] == "test_file2"
    assert cfg.config.format_files[0] == "test_format_file2"
    assert cfg.config.recent_files[1] == "test_file3"
    assert cfg.config.format_files[1] == "test_format_file3"
    assert cfg.config.recent_files[2] == "test_file1"
    assert cfg.config.format_files[2] == "test_format_file_new_1"
    # test get_format_file function
    assert cfg.config.get_format_file("test_file1") == "test_format_file_new_1"
    assert cfg.config.get_format_file("test_file2") == "test_format_file2"
    
    config. update_last_data_dir("/home/test.yaml")
    # test update_last_data_dir
    assert config.last_data_dir == "/home" 
    
    cfg.config.save()
    cfg.config.recent_files = []
    cfg.config.format_files = []
    cfg.config = Config()
    
    # save config
    assert len(cfg.config.format_files) == 3
    assert cfg.config.recent_files[0] == "test_file2"
    assert cfg.config.format_files[0] == "test_format_file2"
    assert cfg.config.recent_files[1] == "test_file3"
    assert cfg.config.format_files[1] == "test_format_file3"
    assert cfg.config.recent_files[2] == "test_file1"
    assert cfg.config.format_files[2] == "test_format_file_new_1"


def test_meconfig_static(request):
    Config.SERIAL_FILE = "ModelEditorData_test"
    cfg.init(None)
    # cfg.config is assigned
    assert cfg.config.__class__== Config
    
    def fin_test_config():
        import config
        config.delete_config_file("ModelEditorData_test")
    request.addfinalizer(fin_test_config)    
  
    cfg.format_files = []
    cfg._read_format_files()
    
    # read format files
    assert len(cfg.format_files) == 2    
    assert 'flow_1.8.2_input_format' in cfg.format_files
    assert '1.8.2' in cfg.format_files
    
    cfg.curr_format_file = None
    cfg.set_current_format_file('flow_1.8.2_input_format')
    # good name
    assert cfg.curr_format_file == 'flow_1.8.2_input_format'
    cfg.set_current_format_file('bad_name')
    # bad name
    assert cfg.curr_format_file == 'flow_1.8.2_input_format'
    
    cfg.document = "#test"
    cfg.changed = True
    cfg.curr_file = "test"
    cfg.new_file()
    # new file test
    assert cfg.document == ""
    assert cfg.changed is False
    assert cfg.curr_file is None
    
    cfg.document = "#test"
    cfg.changed = True
    cfg.curr_file = "test.yaml" 
    cfg.config.add_recent_file("test.yaml","flow_1.8.2_input_format")  
    cfg.save_file()
    
    def fin_test_static():
        import os
        if os.path.isfile("test.yaml"):
            os.remove("test.yaml")
        if os.path.isfile("test2.yaml"):
            os.remove("test2.yaml")
    request.addfinalizer(fin_test_static)    
    
    # save file test
    assert cfg.changed is False
    assert cfg.curr_file == "test.yaml"
    assert cfg.config.recent_files[0] == "test.yaml"
    assert cfg.config.format_files[0] == "flow_1.8.2_input_format"

    cfg.document = "#test2"
    cfg.changed = True
    cfg.save_as("test2.yaml")
    
    #save us test
    assert cfg.changed is False
    assert cfg.curr_file == "test2.yaml"
    assert cfg.config.recent_files[0] == "test2.yaml"
    assert cfg.config.format_files[0] == "flow_1.8.2_input_format"
    assert cfg.config.recent_files[1] == "test.yaml"
    assert cfg.config.format_files[1] == "flow_1.8.2_input_format"
    
    cfg.document = "#test2"
    cfg.changed = True
    cfg.set_current_format_file('1.8.2')    
    
    cfg.open_file("test.yaml")
    #open file test
    assert cfg.changed is False
    assert cfg.curr_file == "test.yaml"
    assert cfg.document == "#test"
    assert cfg.config.recent_files[1] == "test2.yaml"
    assert cfg.config.format_files[1] == "flow_1.8.2_input_format"
    assert cfg.config.recent_files[0] == "test.yaml"
    assert cfg.config.format_files[0] == "1.8.2"
    assert cfg.curr_format_file == '1.8.2'
 
    cfg.document = ""
    cfg.changed = True
    cfg.set_current_format_file('1.8.2')    
    
    cfg.open_recent_file("test2.yaml")
    # open recent file test
    assert cfg.changed is False
    assert cfg.curr_file == "test2.yaml"
    assert cfg.document == "#test2"
    assert cfg.config.recent_files[0] == "test2.yaml"
    assert cfg.config.format_files[0] == "flow_1.8.2_input_format"
    assert cfg.config.recent_files[1] == "test.yaml"
    assert cfg.config.format_files[1] == "1.8.2"
    assert cfg.curr_format_file == 'flow_1.8.2_input_format'    
    
    cfg.update_yaml_file("#new test")
    # test update_yaml_file 1
    assert cfg.changed == True
    assert cfg.document == "#new test"
    
    cfg.changed = False
    cfg.update_yaml_file("#new test")
    # test update_yaml_file 2
    assert cfg.changed is False
    assert cfg.document == "#new test"
