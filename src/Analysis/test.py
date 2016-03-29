from pipeline.parametrized_actions import *
from pipeline.generator_actions import *
from pipeline.wrapper_actions import *
from pipeline.data_types_tree import *
from pipeline.workflow_actions import *
from pipeline.pipeline import *
import pipeline.action_types as action

action.__action_counter__ = 0
items = [
    {'name':'a', 'value':1, 'step':0.1, 'n_plus':1, 'n_minus':1,'exponential':False},
    {'name':'b', 'value':10, 'step':1, 'n_plus':2, 'n_minus':0,'exponential':True} 
]
gen = RangeGenerator(Items=items)    
workflow=Workflow()
flow=Flow123dAction(Input=workflow.input(), Output=String("File"), YAMLFile="test.yaml")
workflow.set_input_action(flow)
workflow.set_output_action(flow)
foreach = ForEach(Input=gen, WrappedAction=workflow)
pipeline=Pipeline(OutputActions=[foreach])
pipeline.inicialize()    
test=pipeline.get_settings_script()
test="\n".join(test)
i=5
