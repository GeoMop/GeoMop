import sys
import os

__an_dir__ = os.path.join(os.path.split(
    os.path.dirname(os.path.realpath(__file__)))[0], "src","Analysis" )

__lib_dir__ = os.path.join(os.path.split(
    os.path.dirname(os.path.realpath(__file__)))[0], "src","common" )
    
sys.path.insert(1, __an_dir__)
sys.path.insert(2, __lib_dir__)

import pytest
code = pytest.main(['-x', 'Analysis'])
sys.exit(code)
