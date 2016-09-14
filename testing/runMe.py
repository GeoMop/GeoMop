import sys
import os

__me_dir__ = os.path.join(os.path.split(
    os.path.dirname(os.path.realpath(__file__)))[0], "src","ModelEditor" )
__lib_dir__ = os.path.join(os.path.split(
    os.path.dirname(os.path.realpath(__file__)))[0], "src","common" )
__mock_dir__ = "./ModelEditor/mock"
    
sys.path.insert(1, __me_dir__)
sys.path.insert(2, __lib_dir__)
sys.path.insert(3, __mock_dir__)

import pytest
pytest.main(['-x', 'ModelEditor'""", '-k',  "not test_transformace.py" """])
