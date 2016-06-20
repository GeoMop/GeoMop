from enum import Enum
import pipeline as p

class ParameterTypes(Enum):
    """
    Action parameter types for UI 
    
    UI can help and check parameter, that 
    afterwards is passed on pipeline as string
    """
    string = 0
    int = 1
    float = 2
    bool = 3
    input_file = 4
    output_file = 5
    gdtt = 6
    dtt = 7
    range_item = 8
    workflow = 9 # for wrapped action
    action = 10
    action_array = 11
    
class ActionTypes(Enum):
    """Action types for ui"""
    base = 0
    connector = 1
    wrapper = 2
    workflow = 3

class ActionParameter:
    """Action settings parameters defination"""
    def __init__(self, name, type, description=""):
        self.config_name = name
        """Parameter name  in config settings"""
        self.name = name
        """Parameter name for ui"""
        self.description = description
        """Parameter name for ui"""
        self.type = type
        """UI interface type for parrameter settings"""
        
class Action:
    """Action data container for ActionsTypes class"""
    def __init__(self, action_class, name,  group, type, max_inputs=-1,  parameters=[],  description=""):
        self.action_class = action_class
        """action class name for instance creation"""
        self.name = name
        """string action name for ui"""
        self.group = group
        """string group action name for ui"""
        self.type = type
        """ui action class"""
        self.max_inputs = max_inputs
        """max number of inputs"""
        self.parameters = parameters
        """array of action parameter types description"""
        self.description = description
        """Parameter name for ui"""

ACTION_TYPES = [
    Action(
        p.Connector, 
        'Connector', 
        'Connectors',
        ActionTypes.connector,
        0,  
        [
            ActionParameter(
                'Convertor', 
                ParameterTypes.gdtt                
            )
        ], 
        p.Connector.description
    ), 
    Action(
        p.VariableGenerator, 
        'Variable Generator',
        'Generators', 
        ActionTypes.base,
        -1,  
        [
            ActionParameter(
                'Variable', 
                ParameterTypes.dtt                
            )
        ], 
        p.VariableGenerator.description
    ), 
    Action(
        p.RangeGenerator, 
        'Range Generator',
        'Generators', 
        ActionTypes.base,
        -1,  
        [
            ActionParameter(
                'Items', 
                ParameterTypes.range_item                
            )
        ], 
        p.RangeGenerator.description
    ),
    Action(
        p.Flow123dAction, 
        'Flow123d',
        'Parametrized', 
        ActionTypes.base,
        -1,  
        [
            ActionParameter(
                'YAMLFile', 
                ParameterTypes. input_file                
            )
        ], 
        p.Flow123dAction.description
    ),
    Action(
        p.Workflow, 
        'Workflow',
        'Workflow', 
        ActionTypes.workflow,
        -1,  
        [
            ActionParameter(
                'InputAction', 
                ParameterTypes.action            
            ), 
            ActionParameter(
                'OutputAction', 
                ParameterTypes.action            
            ), 
            ActionParameter(
                'ResultActions', 
                ParameterTypes.action_array            
            )
        ], 
        p.Workflow.description
    ),
    Action(
        p.ForEach, 
        'ForEach',
        'Wrappers', 
        ActionTypes.wrapper,
        -1,  
        [
            ActionParameter(
                'WrappedAction', 
                ParameterTypes.workflow            
            )
        ], 
        p.ForEach.description
    )
]
