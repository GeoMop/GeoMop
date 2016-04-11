from pipeline.parametrized_actions import *
from pipeline.generator_actions import *
from pipeline.data_types_tree import *
from .pomfce import *
import pipeline.action_types as action
import os

def test_flow_code_init():
    action.__action_counter__ = 0
    input=VariableGenerator(Variable=Struct(test1=String("test")))
    input.inicialize()
    flow=Flow123dAction(Inputs=[input], YAMLFile="test.yaml")
    flow.inicialize()    
    test = input.get_settings_script()
    test.extend(flow.get_settings_script())

    compare_with_file(os.path.join("pipeline", "results", "flow1.py"), test)
    exec ('\n'.join(test), globals())
    VariableGenerator_1.inicialize()
    Flow123d_2.inicialize()    
    
    assert Flow123d_2.variables['YAMLFile'] == flow.variables['YAMLFile']
    assert Flow123d_2.get_input_val(0).test1 == flow.get_input_val(0).test1
    
    
