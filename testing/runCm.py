import sys
import os

__lib_dir__ = os.path.join(os.path.split(
    os.path.dirname(os.path.realpath(__file__)))[0], "src","common" )
    
__root_dir__ = os.getcwd()
    
sys.path.insert(1, __lib_dir__)

import pytest
code = pytest.main("--junitxml=" + os.path.join(__root_dir__, "testCommon.xml") + " common")
sys.exit(code)
