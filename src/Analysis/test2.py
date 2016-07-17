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
pipeline._inicialize()
test = pipeline._get_settings_script()
hlist1 = pipeline._get_hashes_list()

il = IdenticalList({"1": "11", "2": "12", "3": "13", "4": "14"})
pipeline._set_restore_id(il)

assert vg._restore_id == "11"
assert vg2._restore_id == "12"
assert workflow._restore_id == "13"
assert flow._restore_id == "14"
assert side._restore_id == "None"
assert pipeline._restore_id == "None"



print(9)
