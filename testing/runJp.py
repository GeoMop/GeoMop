import sys
import os

__js_dir__ = os.path.join(os.path.split(
    os.path.dirname(os.path.realpath(__file__)))[0], "src","JobPanel" )
__pexpect_dir__ = os.path.join(os.path.split(
    os.path.dirname(os.path.realpath(__file__)))[0], "src","JobPanel", "twoparty", "pexpect" )
__lib_dir__ = os.path.join(os.path.split(
    os.path.dirname(os.path.realpath(__file__)))[0], "src","common" )
__mock_dir__ = "./JobPanel/mock"
    
sys.path.insert(1, __js_dir__)
sys.path.insert(2, __lib_dir__)
sys.path.insert(3, __mock_dir__)
sys.path.insert(4, __pexpect_dir__)

import pytest
pytest.main(['-x', 'JobPanel'])
