from pipeline.convertor_actions import *
from pipeline.generator_actions import *
from pipeline.data_types_tree import *
from pipeline.predicate import *

p1 = Predicate(DefInput=GDTT(Struct)) 
time = (p1.input(0).time > 600) & (p1.input(0).time<1000)
value = (p1.input(0).value > 3.0) | (p1.input(0).value < 1.0)
bc_type = p1.input(0).bc_type == 4
p1.set_config(DefOutput = time & value & bc_type)
    
p2 = Predicate(DefInput=GDTT(Struct)) 
p2.set_config(DefOutput = p2.input(0).value)

test01=p1.get_settings_script()
test02=p2.get_settings_script()

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
k.set_config(DefOutput = Struct(a=a, b=b, c=k.input(2).sort(p2)))

test1=k.get_settings_script()

k.set_inputs([v1, v2, v3])
v1.inicialize()
v2.inicialize()
v3.inicialize()
k.inicialize()

test2=k.get_settings_script()
test3=k.get_output().get_settings_script()

k2 = k.duplicate()
test4=k2.get_settings_script()
k2.inicialize()

test5=k2.get_settings_script()
test6=k2.get_output().get_settings_script()

test=v1.get_settings_script()
test.extend(v2.get_settings_script())
test.extend(v3.get_settings_script())
test.extend(k2.get_settings_script())

script = '\n'.join(test01)

test = 0
