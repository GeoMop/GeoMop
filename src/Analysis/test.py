from pipeline.data_types_tree import *
from pipeline.parametrized_actions import *

var1 = Struct(test1=Int(1), test2=String("Test"))
var2 = Struct(test1=Int(), test2=String(), test3=Int())

ens1 = Ensemble(var1, 
    Struct(test1=Int(1), test2=String("Test1")), 
    Struct(test1=Int(2), test2=String("Test2")), 
    Struct(test1=Int(3), test2=String("Test3"))) 
ens2 = Ensemble(var2, 
    Struct(test1=Int(1), test2=String("Test1"), test3=Int()), 
    Struct(test1=Int(2), test2=String("Test2"), test3=Int()), 
    Struct(test1=Int(3), test2=String("Test3"), test3=Int())) 
    
set = ens1.is_set()
match = ens1.match_type(ens2)  
