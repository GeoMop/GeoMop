from pipeline.parameter_types import *

def test_parameters():
    var1 = Struct(test1=Int(1), test2=String("Test"))
    var2 = Struct(test1=Int(), test2=String(), test3=Int())
    
    assert var1.is_set()
    assert not var1.contain(var2)  
    assert not var2.is_set()
    assert var2.contain(var1)
    
    var1 = Struct(test1=Int(1), test2=String("Test"), tests=Struct(iner1=Int(5)))
    var2 = Struct(test1=Int(), test2=String(), tests=Struct(iner1=Int(),iner2=Int()))
    
    
    assert var1.is_set()
    assert not var1.contain(var2)  
    assert not var2.is_set()
    assert var2.contain(var1)
    
    var2.reduce_keys("test1", "test2")
    var2.test1=5
    var2.test2="ooo"
    test = var2.test1
    test == 5
    assert var2.test1.value == 5
    assert var2.test2.value == "ooo"    
    assert var1.contain(var2)
    var2.test1= var1.test1
    assert var2.test1.value == 1
    
    
    
    
