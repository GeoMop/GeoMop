from pipeline.data_types_tree import *
from pipeline.parametrized_actions import *

flow=Flow123dAction(Input=Struct(test1=String("test")), Output=String("File"), YAMLFile="test.yaml")
test=flow.get_settings_script()
exec('\n'.join(test))
print('\n'.join(test))

var2 = Struct(test1=Int(), test2=String(), tests=Struct(iner1=Int(),iner2=Int()))
var1 = Struct({"test1":Int(),"test2":String(), tests:Struct(iner1=Int(),iner2=Int())})
var2.reduce_keys("test1", "test2")
var2.test1 = 5
var2.test2="ooo"
