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



from geomop_analysis import YamlSupportLocal
#from pipeline.flow_data_types import *
#from flow_util import YamlSupport

#from client_pipeline.identical_list_creator import *

ys = YamlSupportLocal()
err = ys.parse(r"d:\geomop\analysis\GeoMop\testing\Analysis\pipeline/flow_data_types_res/02_2/flow_lin_sorption_dg.yaml")
#ys.save(r"d:\geomop\analysis\GeoMop\testing\Analysis\pipeline\flow_data_types_res\01\flow_gmsh.sprt")



#vg = VariableGenerator(Variable=Struct(a=String("test"), b=Int(3)))
# vg = VariableGenerator(Variable=Struct(par1=String("test"), par2=Int(8)))
# flow = Flow123dAction(Inputs=[vg], YAMLFile="d:/test/flow_gmsh_par.yaml")
#
# vg._inicialize()
# flow._inicialize()
# err = flow.validate()
# runner = flow._update()

b = True


from pipeline.flow_data_types import *


f=FlowOutputType.create_type(ys)
#f=FlowOutputType.create_data(ys, r"d:\geomop\analysis\GeoMop\testing\Analysis\pipeline/flow_data_types_res/21\output")
ss=f._get_settings_script()
tt="\n".join(ss)


print(9)
