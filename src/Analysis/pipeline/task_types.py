import abc
from copy import deepcopy

class Task_types:
    """
    Container for Tasks types
    
    All tasks types have initial configuration, but ther are possibility
    change some configuration dynamicaly. If task types is used, is
    maked it deep coppy, and changis is made to this class.  
    """
    
    def __init__(self):
        self.tasks_types = []
        """dictionary of tasks"""        
        self.used_tasks_types = []
        """iTask"""
        
    def  get_used_task(self, name):
        """create new task acoding set type and ad it to list"""
        for task in self.tasks:
            if name == task.name:
                utask = deepcopy(task)
                self.used_tasks.append(utask)
                return utask
        return None

    def  get_task_list(self):
        """get list all types"""
        list = {}
        for task in self.tasks:
            list[task.name]=task
        return list
        
class Task(metaclass=abc.ABCMeta):
    """
    Abbstract class od tasks, that define tasks method for
    tasks classes
    """
    
    def __init__(self):
        self.name = ""
        """Display name of task"""
        self.description = ""
        """Display description of task"""
        self.in_ports = {}
        """dictionary names => types of input ports"""
        self.out_ports = {}
        """dictionary names => types of output ports"""
        self.variable = {}
        """dictionary names => types of variables"""
        self.errs = []
        """array of validation errors"""
    
    @abc.abstractmethod 
    def run_script(self):    
        """action perl script"""
        pass
