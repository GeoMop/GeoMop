import sys
import os

__an_dir__ = os.path.join(os.path.split(
    os.path.dirname(os.path.realpath(__file__)))[0], "src","Analysis" )

__lib_dir__ = os.path.join(os.path.split(
    os.path.dirname(os.path.realpath(__file__)))[0], "src","common" )

__root_dir__ = os.getcwd()
    
sys.path.insert(0, __an_dir__)
sys.path.insert(2, __lib_dir__)

os.chdir(os.path.join(__root_dir__, "Analysis"))
import pytest

code = pytest.main("--junitxml=" + os.path.join(__root_dir__, "testAn.xml"))
sys.exit(code)
