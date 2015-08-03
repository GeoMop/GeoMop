import mock_transform as mocktrf
import re
import mock_config as mockcfg
from data.yaml.transformator import Transformator, TransformationFileFormatError

def test_init():
    text = ""
    try:
        transformator = Transformator(text)
        "empty file exception"
        assert False
    except (ValueError, TransformationFileFormatError) as err:
        "empty file exception"
        assert str(err) == "Expecting value: line 1 column 1 (char 0)"
    text = mocktrf.load_empty_tranformation_file()
    
    try:
        transformator = Transformator(text)
        "empty path exception"
        assert False
    except (ValueError, TransformationFileFormatError) as err:
        "empty destination_path exception"
        assert str(err) == "Parameter path for action type 'delete-key' cannot be empty (action: 1)"
        
    text = re.sub('"path"\: ""','"path": "/myPath"', text)
    try:
        transformator = Transformator(text)
        "empty path exception"
        assert False
    except (ValueError, TransformationFileFormatError) as err:
        "empty destination_path exception"
        assert str(err) == "Parameter destination_path for action type 'move-key' cannot be empty (action: 2)"
        text = re.sub('"path"\: ""','"path": "/myPath"', text)
        
    text = re.sub('"destination_path"\: ""','"destination_path": "/myPath/dest"', text)
    text = re.sub('"source_path"\: ""','"source_path": "/myPath/source"', text)
    try:
        transformator = Transformator(text)
        "empty new_name exception"
        assert False
    except (ValueError, TransformationFileFormatError) as err:
        "empty new_name exception"
        assert str(err) == "Parameter new_name for action type 'rename-type' cannot be empty (action: 3)"
    text = re.sub('"new_name"\: ""','"new_name": "newName"', text)
    text = re.sub('"old_name"\: ""','"old_name": "oldName"', text)
    try:
        transformator = Transformator(text)
        "ok file"
        assert len(transformator._transformation['actions']) == 3
    except (ValueError, TransformationFileFormatError) as err:
        "ok file"
        assert False
    
def test_transform(request):
    mockcfg.set_empty_config()

    def fin_test_config():
        mockcfg.clean_config()
    request.addfinalizer(fin_test_config)
