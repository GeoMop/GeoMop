from pipeline.parametrized_actions import *
from pipeline.generator_actions import *
from pipeline.wrapper_actions import *
from pipeline.data_types_tree import *
from pipeline.workflow_actions import *
from pipeline.pipeline import *
#from .pomfce import *
import pipeline.action_types as action
import os

# test workflow duplication
action.__action_counter__ = 0
workflow = Workflow()
flow = Flow123dAction(Inputs=[workflow.input()], YAMLFile="test.yaml")
workflow.set_config(OutputAction=flow, InputAction=flow)
vg = VariableGenerator(Variable=Struct(a=String("test"), b=Int(3)))
w1 = workflow.duplicate()
w1.set_inputs([vg])
w2 = workflow.duplicate()
w2.set_inputs([w1])
pipeline = Pipeline(ResultActions=[w2])
pipeline._inicialize()
test = pipeline._get_settings_script()

# compare_with_file(os.path.join("pipeline", "results", "workflow5.py"), test)

# test validation
err = pipeline.validate()
# assert len(err) == 0

ts=""
for line in test:
    ts += line + "\n"

print(9)
