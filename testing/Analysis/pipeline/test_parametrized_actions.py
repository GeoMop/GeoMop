from pipeline.parametrized_actions import *
from pipeline.data_types_tree import *
from .pomfce import *
import pipeline.action_types as action
import os

def test_flow_code_init():
    action.__action_counter__ = 0
    flow=Flow123dAction(Input=Struct(test1=String("test")), Output=String("File"), YAMLFile="test.yaml")
    flow.inicialize()
    test=flow.get_settings_script()
    compare_with_file(os.path.join("pipeline", "results", "flow1.py"), test)
    exec ('\n'.join(test), globals())
    assert Flow123d_1.variables['YAMLFile'] == flow.variables['YAMLFile']
    assert Flow123d_1.inputs[0].test1 == flow.inputs[0].test1
    assert Flow123d_1.outputs[0] == flow.outputs[0]
    
    
