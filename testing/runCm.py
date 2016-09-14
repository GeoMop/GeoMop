import sys
import os

__lib_dir__ = os.path.join(os.path.split(
    os.path.dirname(os.path.realpath(__file__)))[0], "src","common" )
    
sys.path.insert(1, __lib_dir__)

import pytest
pytest.main(['-x', 'common'])
