import os
import sys
import re

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
from pipeline.connector_actions import *
from pipeline.convertors import *













from geomop_analysis import YamlSupportLocal
#from pipeline.flow_data_types import *
#from flow_util import YamlSupport

#from client_pipeline.identical_list_creator import *

#ys = YamlSupportLocal()
#err = ys.parse(r"d:\geomop\analysis\GeoMop\testing\Analysis\pipeline/flow_data_types_res/02_2/flow_lin_sorption_dg.yaml")
#ys.save(r"d:\geomop\analysis\GeoMop\testing\Analysis\pipeline\flow_data_types_res\01\flow_gmsh.sprt")



#vg = VariableGenerator(Variable=Struct(a=String("test"), b=Int(3)))
# vg = VariableGenerator(Variable=Struct(par1=String("test"), par2=Int(8)))
# flow = Flow123dAction(Inputs=[vg], YAMLFile="d:/test/flow_gmsh_par.yaml")
#
# vg._inicialize()
# flow._inicialize()
# err = flow.validate()
# runner = flow._update()

print(__file__)
print(os.path.realpath(__file__))


ys = YamlSupportLocal()
#err = ys.parse("d:/test/1/test_output.yaml")


#err = ys.parse("d:/test/cal/moje/V7_jb_par.yaml")
#ys.save("d:/test/cal/moje/V7_jb_par.sprt")

# vg = VariableGenerator(Variable=Struct(cond=String("0.07270788")))
# flow = Flow123dAction(Inputs=[vg], YAMLFile="d:/test/cal/moje/V7_jb_par.yaml")
#
# vg._inicialize()
# flow._inicialize()
# err = flow.validate()
# runner = flow._update()






import numpy as np
from scipy.optimize import minimize


x = np.array([1])
y = np.array([1])

q= x == y



from client_pipeline.mj_preparation import *

action.__action_counter__ = 0
items = [
    {'name': 'a', 'value': 1, 'step': 0.1, 'n_plus': 1, 'n_minus': 1, 'exponential': False},
    {'name': 'b', 'value': 10, 'step': 1, 'n_plus': 2, 'n_minus': 0, 'exponential': True}
]
#gen = RangeGenerator(Items=items)
gen = VariableGenerator(Variable=Ensemble(Struct(cond=Float()), Struct(cond=Float(0.06)), Struct(cond=Float(0.07)), Struct(cond=Float(0.08))))
workflow = Workflow()
flow = Flow123dAction(Inputs=[workflow.input()], YAMLFile="V7_jb_par.yaml")
gen2 = VariableGenerator(Variable=Struct(cond=Float(0.09)))
flow2 = Flow123dAction(Inputs=[gen2], YAMLFile="V7_jb_par.yaml")
workflow.set_config(OutputAction=flow, InputAction=flow, ResultActions=[flow2])
foreach = ForEach(Inputs=[gen], WrappedAction=workflow)
pipeline = Pipeline(ResultActions=[foreach])
#flow._output = String()
pipeline._inicialize()
test = pipeline._get_settings_script()
tt="\n".join(test)






err = MjPreparation.prepare(workspace="d:/test/ws", analysis="an2", mj="mj1", python_script="s.py", pipeline_name="Pipeline_5", last_analysis="an1")





from pipeline.flow_data_types import *


#f=FlowOutputType.create_type(ys)
f=FlowOutputType.create_data(ys, r"d:\test\1\output")
ss=f._get_settings_script()
tt="\n".join(ss)


print(9)
