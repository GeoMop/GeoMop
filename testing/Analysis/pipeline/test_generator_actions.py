from pipeline.generator_actions import *
from pipeline.data_types_tree import *
from .pomfce import *
import pipeline.action_types as action
import os

def test_flow_code_init():
    output = Ensemble(Struct(a=Int(1), b=Int(10)))
    items = [
        {'name':'a', 'value':1, 'step':0.1, 'n_plus':1, 'n_minus':1,'exponential':False},
        {'name':'b', 'value':10, 'step':1, 'n_plus':2, 'n_minus':3,'exponential':True} 
    ]
    action.__action_counter__ = 0
    gen=RangeGenerator(Output=output, Items=items)
    test=gen.get_settings_script()
    compare_with_file(os.path.join("pipeline", "results", "gen1.py"), test)
    exec ('\n'.join(test), globals())
    assert Flow123d_1.variables['YAMLFile'] == flow.variables['YAMLFile']
    assert Flow123d_1.inputs[0].test1 == flow.inputs[0].test1
    assert Flow123d_1.output == flow.output
    
    
