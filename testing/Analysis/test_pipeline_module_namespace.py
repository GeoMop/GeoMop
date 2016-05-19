from pipeline import *

def test_data_classes():
    try:
        Int()
        Bool()
        Float()
        String()
        Struct()
        Ensemble(Int())
        And(Bool(True), Bool(False))
        Or(Bool(True), Bool(False))
        Input()
        Connector()
        RangeGenerator()
        VariableGenerator()
        Flow123dAction()
        Convertor(Input(0))
        Predicate(Input(0))
        KeyConvertor(Input(0))
        Adapter(Input(0))
        Pipeline()
        Workflow()
        ForEach()
    except:
        assert False, "All public classes are not vissible"
    
    for types in (
        "DTT", "BaseDTT", "CompositeDTT", "CompositiIter", "SortableDTT"
        "PredicatePoint", "TT", "GDTT_Operators", "GDTT",  " GDTTFunc", 
        "Bridge", " ActionType", "ActionStateType", "BaseActionType", 
        "ConnectorActionType", "  GeneratorActionType", "ParametrizedActionType", 
        "WrapperActionType", "WorkflowActionType", 

    ):
        try:
            test = eval(types+"()")
        except:
            continue
        assert test is None , "Private module class {0} is vissible".format(types)
