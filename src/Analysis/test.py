from pipeline.parametrized_actions import *
from pipeline.generator_actions import *
from pipeline.wrapper_actions import *
from pipeline.data_types_tree import *
from pipeline.workflow_actions import *
from pipeline.pipeline import *
import pipeline.action_types as action

action.__action_counter__ = 0
input=VariableGenerator(Variable=Struct(test1=String("test")))
input.inicialize()
flow=Flow123dAction(Inputs=[input], YAMLFile="test.yaml")
flow.inicialize()    
test = input.get_settings_script()
test.extend(flow.get_settings_script())
test="\n".join(test)
exec ('\n'.join(test), globals())

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
pipeline.inicialize()    
test=pipeline.get_settings_script()
test="\n".join(test)
test=foreach.get_output()
i=5
