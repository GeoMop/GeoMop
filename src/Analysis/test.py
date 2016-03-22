from pipeline.parametrized_actions import *
from pipeline.generator_actions import *
from pipeline.wrapper_actions import *
from pipeline.data_types_tree import *
from pipeline.workflow_actions import *
import pipeline.action_types as action

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
list = workflow._get_child_list()
test=workflow.get_settings_script()
test="\n".join(test)
i=5


