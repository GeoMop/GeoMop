from data_types_tree import *

var2 = Struct(test1=Int(), test2=String(), tests=Struct(iner1=Int(),iner2=Int()))
var1 = Struct({"test1":Int(),"test2":String(), tests:Struct(iner1=Int(),iner2=Int())})
var2.reduce_keys("test1", "test2")
var2.test1 = 5
var2.test2="ooo"
