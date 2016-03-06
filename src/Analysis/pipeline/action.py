class Action():
    """
    Class for action type instance and running information
    """
    def __init__(self, action_type):
        self.action_type =action_type
        """Action type for creation of action"""
        self.errs = []
        """array of validation errors"""
