from pipeline.connector_actions import *
from pipeline.generator_actions import *
from pipeline.data_types_tree import *
from pipeline.generic_tree import *
from pipeline.convertors import *

time = And(Input(0).time > 600,Input(0).time<1000)
value = Or(Input(0).value > 3.0, Input(0).value < 1.0)
bc_type = Input(0).bc_type == 4
p1 = Predicate(And( time, value, bc_type)) 
c1 = KeyConvertor(Input(0).value) 

test01=p1._get_settings_script()
test02=c1._get_settings_script()

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

k = Connector()    
a = Input(0).a
b = Input(1).b
# for later using
k3 = k.duplicate()    
adap = Adapter(Struct(a=Struct(a=Input(0).a), b=Struct(a=Input(0).value)))
conv = Convertor(Struct(a=a, b=b, c=Input(2).each(adap)))
k.set_config(Convertor = conv)

test1=k._get_settings_script()

k.set_inputs([v1, v2, v3])
v1._inicialize()
v2._inicialize()
v3._inicialize()
k._inicialize()

errs = conv._check_params([v1, v2, v3])

test2=k._get_settings_script()
test3=k._get_output()._get_settings_script()

struc = k._get_output()

k2 = k.duplicate()
test4=k2._get_settings_script()
k2._inicialize()

test5=k2._get_settings_script()
test6=k2._get_output()._get_settings_script()

test=v1._get_settings_script()
test.extend(v2._get_settings_script())
test.extend(v3._get_settings_script())
test.extend(k2._get_settings_script())

exec ('\n'.join(test), globals())    
VariableGenerator_1._inicialize()
VariableGenerator_2._inicialize()
VariableGenerator_3._inicialize()

Conn_14._inicialize()
testx3=Conn_14._get_output()._get_settings_script()

script = '\n'.join(testx3)

test = 0
