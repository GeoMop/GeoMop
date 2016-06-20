from pipeline.parametrized_actions import *
from pipeline.generator_actions import *
from pipeline.wrapper_actions import *
from pipeline.data_types_tree import *
from pipeline.workflow_actions import *
from pipeline.pipeline import *
#from .pomfce import *
import pipeline.action_types as action
import os

# test workflow v 2xForEach in each other
action.__action_counter__ = 0
items = [
    {'name': 'a', 'value': 1, 'step': 0.1, 'n_plus': 1, 'n_minus': 1, 'exponential': False},
    {'name': 'b', 'value': 10, 'step': 1, 'n_plus': 2, 'n_minus': 0, 'exponential': True}
]
items2 = [
    {'name': 'x', 'value': 1, 'step': 0.1, 'n_plus': 1, 'n_minus': 1, 'exponential': False},
    {'name': 'y', 'value': 10, 'step': 1, 'n_plus': 2, 'n_minus': 0, 'exponential': True}
]
gen = RangeGenerator(Items=items)
gen2 = RangeGenerator(Items=items2)
workflow = Workflow()
workflow2 = Workflow()
flow = Flow123dAction(Inputs=[workflow2.input()], YAMLFile="test.yaml")
workflow2.set_config(OutputAction=flow, InputAction=flow)
foreach2 = ForEach(Inputs=[gen2], WrappedAction=workflow2)
workflow.set_config(OutputAction=foreach2, InputAction=foreach2)
foreach = ForEach(Inputs=[gen], WrappedAction=workflow)
pipeline = Pipeline(ResultActions=[foreach])
flow._output = String()
pipeline._inicialize()
test = pipeline._get_settings_script()


# test validation
err = workflow.validate()
# assert len(err) == 0

ts=""
for line in test:
    ts += line + "\n"
