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
    workflow = 7 # for wrapped action
    
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
    def __init__(self, action_class, name, type, max_inputs=-1,  parameters=[],  description=""):
        self.action_class = action_class
        """action class name for instance creation"""
        self.name = name
        """string action name for ui"""
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
        ActionTypes.connector,
        -1,  
        [
            ActionParameter(
                'Convertor', 
                ParameterTypes.gdtt                
            )
        ], 
        p.Connector.description
    )
]
