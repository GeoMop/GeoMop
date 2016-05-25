from pipeline.connector_actions import *
from pipeline.generator_actions import *
from pipeline.data_types_tree import *
from pipeline.generic_tree import *
from pipeline.convertors import *
from pipeline.pipeline_processor import *
from pipeline.pipeline import *
from pipeline.workflow_actions import *
from pipeline.wrapper_actions import *
from pipeline.parametrized_actions import *
import pipeline.action_types as action
import time
import shutil

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
pp = Pipelineprocessor(pipeline)
errs = pp.validate()
pp.run()
while pp.is_run():
    runner = pp.get_next_job()
    if runner is None:
        time.sleep(1)
    else:
        print(runner.name+"\n")
        pp.set_job_finished(runner.id)
test = foreach._get_output()
shutil.rmtree("backup", ignore_errors=True)
i=0
