from pipeline.convertor_actions import *
from pipeline.data_types_tree import *

k = CommonConvertor(DefInputs=[GDTT(Struct), GDTT(Struct), GDTT(Ensemble)])    
a = k.input(0).a
b = k.input(1).b
k.set_config(Output = Struct(a=a, b=b))

test=k.get_settings_script()
test = 0
