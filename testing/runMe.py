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

__root_dir__ = os.getcwd()

import pytest
code = pytest.main("--junitxml=" + os.path.join(__root_dir__, "testMe.xml") + " ModelEditor")#""", '-k'  "not test_transformace.py" """])
sys.exit(code)
