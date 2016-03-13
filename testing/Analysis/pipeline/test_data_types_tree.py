from pipeline.data_types_tree import *

def test_struc():
    var1 = Struct(test1=Int(1), test2=String("Test"))
    var2 = Struct(test1=Int(), test2=String(), test3=Int())
    
    assert var1.is_set()
    assert var1.match_type(var2)  
    assert not var2.is_set()
    assert not var2.match_type(var1)
    
    var1 = Struct(test1=Int(1), test2=String("Test"), tests=Struct(iner1=Int(5)))
    var2 = Struct(test1=Int(), test2=String(), tests=Struct(iner1=Int(),iner2=Int()))
    
    
    assert var1.is_set()
    assert not var1.match_type(var2)  
    assert not var2.is_set()
    assert var2.match_type(var1)
    
    var2.test1=5
    var2.test2="ooo"
    test = var2.test1
    test == 5
    assert var2.test1.value == 5
    assert var2.test2.value == "ooo"    
    assert var2.match_type(var1)
    var2.test1= var1.test1
    assert var2.test1.value == 1

def test_ensemble():    
    var1 = Struct(test1=Int(1), test2=String("Test"))
    var2 = Struct(test1=Int(), test2=String(), test3=Int())
    try:
        ens1 = Ensemble(var1, 
            Struct(test1=Int(1), test2=String("Test1")), 
            Struct(test1=Int(2), test2=String("Test2")), 
            Struct(test1=String('Bad type'), test2=String("Test3"))) 
        assert False, "Raise type exception fail"
    except Exception as err:
        assert str(err)[:27]=='Not supported ensemble type'
        
    try:
        ens1 = Ensemble(var1, 
            Struct(test1=Int(1), test2=String("Test1")), 
            Struct(test1=Int(2), test2=String("Test2")), 
            8)
        assert False, "Raise DTT exception fail"
    except Exception as err:
        assert str(err)=='Ensemble must have DTT value type.'

    ens1 = Ensemble(var1, 
        Struct(test1=Int(1), test2=String("Test1")), 
        Struct(test1=Int(2), test2=String("Test2")), 
        Struct(test1=Int(3), test2=String("Test3"))) 
    ens2 = Ensemble(var2, 
        Struct(test1=Int(1), test2=String("Test1"), test3=Int()), 
        Struct(test1=Int(2), test2=String("Test2"), test3=Int()), 
        Struct(test1=Int(3), test2=String("Test3"), test3=Int())) 
        
    assert ens1.is_set()
    assert ens1.match_type(ens2)  
    assert not ens2.is_set()
    assert not ens2.match_type(ens1)
        
