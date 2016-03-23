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
    workflow=Workflow(InputAction=gen, OutputAction=foreach)
    workflow.inicialize()    
    test=workflow.get_settings_script()
    
    compare_with_file(os.path.join("pipeline", "results", "workflow1.py"), test)
    exec ('\n'.join(test), globals())
    assert Flow123d_3.variables['YAMLFile'] == flow.variables['YAMLFile']
    
    # test validation
    err = gen.validate()
    assert len(err)==0
 
    # check output types directly
    assert isinstance(gen.get_output( foreach, 0), Ensemble)
    assert isinstance(gen.get_output( foreach, 0).subtype, Struct)
    assert isinstance(foreach.get_output( workflow, 0), Ensemble)
    assert isinstance(foreach.get_output( workflow, 0).subtype, String)
    assert isinstance(foreach.get_output( flow, 0), Struct)
    assert 'a' in foreach.get_output( flow, 0)
    assert 'b' in foreach.get_output( flow, 0)
    assert 'c' not in foreach.get_output( flow, 0)    
    assert isinstance(flow.get_output( workflow, 0), String)
    assert isinstance(workflow.get_output( workflow, 0).subtype, String)
