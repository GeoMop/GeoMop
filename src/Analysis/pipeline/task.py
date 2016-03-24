class Variable:
    """Port class"""
    def __init__(self, name,  type, value):
        self.name = name
        """Name, that is transform to variable"""
        self.type = type
        """Variable type"""
        self.value = value
        """Variable value"""

class Task():
    """
    Task
    """

    def __init__(self, type):
        self.task_type = type
        """Display description of port"""
        self.task_variables = []
        """arrays for variables, out and in ports type Variables"""
        
    def set_input_variables(self, in_variables):
        """
        check variables type and add it to task_variables
        
        :in_variables: Dictionry name => value of global variables
        """
        pass

    def _instantiate(self):
        """
        check get parameters and dynamicaly make perl 
        code for class variables
        """
        code = ""
        #ToDo variables init
        code += self.task_type.run_script()
        return code
