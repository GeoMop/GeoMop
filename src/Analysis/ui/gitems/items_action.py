from enum import Enum

class RequiredAction(Enum):
    """
    Action that scene should manage for current node
    """    
    no_action = 0
    conn_add = 1
    conn_move = 2
    conn_delete = 3
    node_focus = 4
    node_menu = 5    

class ItemsAction():
    """
    Class that is pass on item by scene. Item
    fill itself and required action
    """
    def __init__(self):
        self.item = None
        """processed item"""
        self.action = RequiredAction.no_action
        """action"""
