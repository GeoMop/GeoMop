from pipeline.convertor_actions import *
from pipeline.generator_actions import *
from pipeline.data_types_tree import *

v1 = VariableGenerator(Variable=Struct(a=String("test"), b=Int(3)))
v2 = VariableGenerator(Variable=Struct(a=String("test new"), b=Int(8)))
v3 = VariableGenerator(Variable=Ensemble(
    Struct(a=String(), time=Int(), value = Float(), bc_type=Int()),
    Struct(a=String("a1"), time=Int(500), value = Float(5.0), bc_type=Int(4)), 
    Struct(a=String("a2"), time=Int(650), value = Float(2.0), bc_type=Int(4)),
    Struct(a=String("a3"), time=Int(700), value = Float(8.0), bc_type=Int(3)),
    Struct(a=String("a4"), time=Int(750), value = Float(12.0), bc_type=Int(4)),
    Struct(a=String("a5"), time=Int(850), value = Float(2.0), bc_type=Int(3)),
    Struct(a=String("a6"), time=Int(900), value = Float(13.0), bc_type=Int(4)),
    Struct(a=String("a7"), time=Int(1100), value = Float(18.0), bc_type=Int(6)),
))

k = CommonConvertor(DefInputs=[GDTT(Struct), GDTT(Struct), GDTT(Ensemble)])    
a = k.input(0).a
b = k.input(1).b
k.set_config(DefOutput = Struct(a=a, b=b, c=k.input(2)))

test1=k.get_settings_script()

k.set_inputs([v1, v2, v3])
v1.inicialize()
v2.inicialize()
v3.inicialize()
k.inicialize()

test2=k.get_settings_script()
test3=k.get_output().get_settings_script()

test = 0
