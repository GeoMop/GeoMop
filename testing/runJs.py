import sys
import os

__js_dir__ = os.path.join(os.path.split(
    os.path.dirname(os.path.realpath(__file__)))[0], "src","JobsScheduler" )
__pexpect_dir__ = os.path.join(os.path.split(
    os.path.dirname(os.path.realpath(__file__)))[0], "src","JobsScheduler", "twoparty", "pexpect" )
__lib_dir__ = os.path.join(os.path.split(
    os.path.dirname(os.path.realpath(__file__)))[0], "src","common" )
__mock_dir__ = "./JobsScheduler/mock"
    
sys.path.insert(1, __js_dir__)
sys.path.insert(2, __lib_dir__)
sys.path.insert(3, __mock_dir__)
sys.path.insert(4, __pexpect_dir__)

import pytest
pytest.main(['-x', 'JobsScheduler'])
