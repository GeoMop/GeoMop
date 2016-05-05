from pipeline.connector_actions import *
from pipeline.generator_actions import *
from pipeline.data_types_tree import *
from pipeline.generic_tree import *
from pipeline.convertors import *

action.__action_counter__ = 0
items = [
    {'name':'a', 'value':1, 'step':0.1, 'n_plus':1, 'n_minus':1,'exponential':False},
    {'name':'b', 'value':10, 'step':1, 'n_plus':2, 'n_minus':0,'exponential':True} 
]
gen = RangeGenerator(Items=items)    
workflow=Workflow()
flow=Flow123dAction(Inputs=[workflow.input()], YAMLFile="test.yaml")
workflow.set_config(OutputAction=flow, InputAction=flow)
foreach = ForEach(Inputs=[gen], WrappedAction=workflow)
pipeline=Pipeline(ResultActions=[foreach])
pipeline._inicialize()
