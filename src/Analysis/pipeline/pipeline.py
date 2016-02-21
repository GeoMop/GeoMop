class GlobalVariables:
    """variable unique namespace"""
    class LocalVariable:
        def __init__(self, task,  name):
            self.task = task
            """task name"""
            self.name = name
            """local variable name"""

    def __init__(self):        
        self.variables_names = []
        """global namespace"""
        self.aliases = {}
        """Dictionary alias => local name"""
        
    def is_used(self, name):
        """return if variable is in global namespace"""
        return name in self.variables_names
        
    def add_alias(self, task, task_name, global_name):
        """Add alias to global namespace"""
        self.add_variable(global_name)
        self.aliases[global_name] = self.LocalVariable(task, task_name)
        
    def add_variable(self, name):
        """Add variable to global namespace"""
        if self.is_used(name):
            raise Exception("Global variable {0} is already used".format(name))
        self.variables_names.append(name)
        
    def to_global(self, task, local_dict, global_dict):
        """add local variable to global dictionary"""
        for local in local_dict:
            in_alias = False
            for alias in self.aliases:
                if self.aliases[alias].name == local and task == self.aliases[alias].task:
                    in_alias = True
                    global_dict[alias] = local_dict[local]
                    break
            if not in_alias:
                global_dict[local] = local_dict[local]
        
    def to_local(self, task, local_dict, global_dict):
        """add local variable to global dictionary"""
        for local in local_dict:
            in_alias = False
            for alias in self.aliases:
                if self.aliases[alias].name == local and task == self.aliases[alias].task:
                    in_alias = True
                    local_dict[local] = global_dict[alias] 
                    break
            if not in_alias:
                local_dict[local] = global_dict[local] 

class PipeLine:
    """
    Pipeline base type
    """
    
    def __init__(self):
        self.tasks = []
        """Array of tasks"""
        
