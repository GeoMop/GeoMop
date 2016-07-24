import os
import sys

__lib_dir__ = os.path.join(os.path.split(
    os.path.dirname(os.path.realpath(__file__)))[0], "common")
sys.path.insert(1, __lib_dir__)

from pipeline.parametrized_actions import *
from pipeline.generator_actions import *
from pipeline.wrapper_actions import *
from pipeline.data_types_tree import *
from pipeline.workflow_actions import *
from pipeline.pipeline import *
from pipeline.pipeline_processor import *
from pipeline.identical_list import *
#from .pomfce import *
import pipeline.action_types as action



#from geomop_analysis import YamlSupport

from client_pipeline.identical_list_creator import *

action.__action_counter__ = 0
vg = VariableGenerator(Variable=Struct(a=String("test"), b=Int(3)))
vg2 = VariableGenerator(Variable=Struct(a=String("test2"), b=Int(5)))
workflow = Workflow(Inputs=[vg2])
flow = Flow123dAction(Inputs=[workflow.input()], YAMLFile="test.yaml")
side = Flow123dAction(Inputs=[vg], YAMLFile="test2.yaml")
workflow.set_config(OutputAction=flow, InputAction=flow, ResultActions=[side])
pipeline = Pipeline(ResultActions=[workflow])
#pipeline._inicialize()


pp = Pipelineprocessor(pipeline)
errs = pp.validate()

names = []
pp.run()
i = 0

while pp.is_run():
    runner = pp.get_next_job()
    if runner is None:
        time.sleep(0.1)
    else:
        names.append(runner.name)
        pp.set_job_finished(runner.id)
    i += 1
    assert i < 1000, "Timeout"

print(9)
