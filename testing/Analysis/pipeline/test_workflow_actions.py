from pipeline.parametrized_actions import *
from pipeline.generator_actions import *
from pipeline.wrapper_actions import *
from pipeline.data_types_tree import *
from pipeline.workflow_actions import *
from .pomfce import *
import pipeline.action_types as action
import os

def test_workflow_code_init():
    action.__action_counter__ = 0
    items = [
        {'name':'a', 'value':1, 'step':0.1, 'n_plus':1, 'n_minus':1,'exponential':False},
        {'name':'b', 'value':10, 'step':1, 'n_plus':2, 'n_minus':0,'exponential':True} 
    ]
    gen = RangeGenerator(Items=items)
    foreach = ForEach(Input=gen)
    flow=Flow123dAction(Input=foreach, Output=String("File"), YAMLFile="test.yaml")
    foreach.set_wrapped_action(flow)
    workflow=Workflow(Input=String("test"), Output=foreach)
    workflow.inicialize()    
    test=workflow.get_settings_script()
    
#    compare_with_file(os.path.join("pipeline", "results", "workflow1.py"), test)
#    exec ('\n'.join(test), globals())
#    assert Flow123d_1.variables['YAMLFile'] == flow.variables['YAMLFile']
#    assert Flow123d_1.inputs[0].test1 == flow.inputs[0].test1
#    assert Flow123d_1.output == flow.output
    
    
