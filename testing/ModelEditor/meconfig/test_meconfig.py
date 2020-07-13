"""
Tests for the meconfig module.
"""

import pytest

from ModelEditor.meconfig import MEConfig as cfg
from ModelEditor.meconfig import _Config as Config

def test_config(request):
    Config.SERIAL_FILE = "ModelEditorData_test"
    cfg.init(None)
    cfg.config = Config()
    # cfg.config is assigned
    assert cfg.config.__class__ == Config

    def fin_test_config():
        import gm_base.config
        gm_base.config.delete_config_file("ModelEditorData_test")
    request.addfinalizer(fin_test_config)

    import os
    cwd = os.getcwd()
    # current_working_dir for first opened config is cwd
    assert cwd == cfg.config.current_working_dir
    config = Config()
    # new config have current_working_dir == cwd
    assert cwd == config.current_working_dir

    cfg.config.add_recent_file("test_file1", "test_format_file1")
    # add first file
    assert cfg.config.recent_files[0] == "test_file1"
    assert cfg.config.format_files[0] == "test_format_file1"

    cfg.config.add_recent_file("test_file1", "test_format_file_new_1")
    # change only format
    assert cfg.config.format_files[0] == "test_format_file_new_1"
    assert len(cfg.config.format_files) == 1

    cfg.config.add_recent_file("test_file2", "1.8.3")
    cfg.config.add_recent_file("test_file3", "test_format_file3")
    # add 3 files
    assert len(cfg.config.format_files) == 3
    assert cfg.config.recent_files[0] == "test_file3"
    assert cfg.config.format_files[0] == "test_format_file3"
    assert cfg.config.recent_files[2] == "test_file1"
    assert cfg.config.format_files[2] == "test_format_file_new_1"

    cfg.config.add_recent_file("test_file2", "1.8.3")
    # move 2 to first line
    assert len(cfg.config.format_files) == 3
    assert cfg.config.recent_files[0] == "test_file2"
    assert cfg.config.format_files[0] == "1.8.3"
    assert cfg.config.recent_files[1] == "test_file3"
    assert cfg.config.format_files[1] == "test_format_file3"
    assert cfg.config.recent_files[2] == "test_file1"
    assert cfg.config.format_files[2] == "test_format_file_new_1"
    # test get_format_file function
    assert cfg.config.get_format_file("test_file1") == "test_format_file_new_1"
    assert cfg.config.get_format_file("test_file2") == "1.8.3"

    config. update_current_working_dir("/home/test.yaml")
    # test update_current_working_dir
    assert config.current_working_dir == "/home"

    cfg.config.save()
    cfg.config.recent_files = []
    cfg.config.format_files = []
    cfg.config = Config().open()

    # save config
    assert len(cfg.config.format_files) == 3
    assert cfg.config.recent_files[0] == "test_file2"
    assert cfg.config.format_files[0] == "1.8.3"
    assert cfg.config.recent_files[1] == "test_file3"
    assert cfg.config.format_files[1] == "test_format_file3"
    assert cfg.config.recent_files[2] == "test_file1"
    assert cfg.config.format_files[2] == "test_format_file_new_1"


@pytest.mark.skip(reason="not working")
def test_meconfig_static(request):
    Config.SERIAL_FILE = "ModelEditorData_test"
    cfg.init(None)
    # cfg.config is assigned
    assert cfg.config.__class__ == Config

    def fin_test_config():
        import gm_base.config
        gm_base.config.delete_config_file("ModelEditorData_test")
    request.addfinalizer(fin_test_config)

    cfg.format_files = []
    cfg._read_format_files()

    # read format files
    assert '1.8.3' in cfg.format_files

    cfg.curr_format_file = None
    cfg.set_current_format_file('1.8.3')
    # good name
    assert cfg.curr_format_file == '1.8.3'
    cfg.set_current_format_file('bad_name')
    # bad name
    assert cfg.curr_format_file == '1.8.3'

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
    cfg.config.add_recent_file("test.yaml", "1.8.3")
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
    assert cfg.config.format_files[0] == "1.8.3"

    cfg.document = "#test2"
    cfg.changed = True
    cfg.save_as("test2.yaml")

    # save us test
    assert cfg.changed is False
    assert cfg.curr_file == "test2.yaml"
    assert cfg.config.recent_files[0] == "test2.yaml"
    assert cfg.config.format_files[0] == "1.8.3"
    assert cfg.config.recent_files[1] == "test.yaml"
    assert cfg.config.format_files[1] == "1.8.3"

    cfg.document = "#test2"
    cfg.changed = True
    cfg.set_current_format_file('1.8.3')

    cfg.open_file("test.yaml")
    # open file test
    assert cfg.changed is False
    assert cfg.curr_file == "test.yaml"
    assert cfg.document == "#test"
    assert cfg.config.recent_files[1] == "test2.yaml"
    assert cfg.config.format_files[1] == "1.8.3"
    assert cfg.config.recent_files[0] == "test.yaml"
    assert cfg.config.format_files[0] == "1.8.3"
    assert cfg.curr_format_file == '1.8.3'

    cfg.document = ""
    cfg.changed = True
    cfg.set_current_format_file('1.8.3')

    cfg.open_recent_file("test2.yaml")
    # open recent file test
    assert cfg.changed is False
    assert cfg.curr_file == "test2.yaml"
    assert cfg.document == "#test2"
    assert cfg.config.recent_files[0] == "test2.yaml"
    assert cfg.config.format_files[0] == "1.8.3"
    assert cfg.config.recent_files[1] == "test.yaml"
    assert cfg.config.format_files[1] == "1.8.3"
    assert cfg.curr_format_file == '1.8.3'

    cfg.update_yaml_file("#new test")
    # test update_yaml_file 1
    assert cfg.changed == True
    assert cfg.document == "#new test"

    cfg.changed = False
    cfg.update_yaml_file("#new test")
    # test update_yaml_file 2
    assert cfg.changed is False
    assert cfg.document == "#new test"

    # test document parsing
    cfg.document = "n: 1"
    cfg.update()
    assert cfg.root.children[0].value == 1
