import os
import sys
import imp
import traceback
from typing import Callable
from types import ModuleType

from common.analysis.code import wrap
from common.analysis import action_workflow as wf
from common.analysis import data
from common.analysis import action_base
from common.analysis.action_instance import ActionInstance

class InterpreterError(Exception): pass

def my_exec(cmd, globals=None, locals=None, description='source string'):
    try:
        exec(cmd, globals, locals)
    except SyntaxError as err:
        error_class = err.__class__.__name__
        detail = err.args[0] if err.args else None
        line_number = err.lineno

        raise InterpreterError("%s at line %d of %s: %s" % (error_class, line_number, description, detail))
    except Exception as err:
        error_class = err.__class__.__name__
        detail = err.args[0] if err.args else None
        etype, exc, tb = sys.exc_info()
        line_number = traceback.extract_tb(tb)[-1][1]

        traceback.print_exception(etype, exc, tb)
        raise InterpreterError("%s at line %d of %s: %s" % (error_class, line_number, description, detail))
    #else:
    #    return



class Module:
    """
    Object representing a module (whole file) that can contain
    several worflow and converter definitions and possibly also a script itself.
    Module is used just to capture the code and do not participate on exectution in any way.
    Underlying python module is responsible.

    We  inspect __dict__ of the loaded module to find all definitions.
    The script must be a workflow function decorated with @analysis decorator.

    Only objects decorated by one of decorators from code.decorators are captured,
    remaining code is ignored. Possible non-workflow actions can be used but
    their code can not be reproduced. In order to do not break the code we prevent
    saving of the generated code to the original file.

    Captured object are stored in the list self.definitions which can be
    """


    @staticmethod
    def catch_object(name, object):
        """
        Predicate to identify Analysis definitions in the modlue dict.
        TODO: possibly catch without decorators
        Currently:
        - ignore underscored names
        - ignore non-classes
        - ignore classes not derived from _ActionBase
        - print all non-underscore ignored names
        """


    def __init__(self, module_file: str) -> None:
        """
        Constructor of the _Module wrapper.
        :param module: a python module object
        """
        self.module_file = module_file
        # File with the module source code.
        self.module = self.load_module(module_file)
        # Ref to wrapped python module object.

        self.definitions = []
        # Actions defined in the module. Includes:
        # Workflows, python source actions (GUI can not edit modules with these actions),
        # data classes, enums.
        # GUI note: Can be directly reorganized by the GUI. Adding, removing, changing order.
        # TODO: implement a method for sorting the definitions (which criteria)
        self._name_to_def = {}
        # Maps identifiers to the definitions. (e.g. name of a workflow to its object)

        self.imported_modules = []
        # List of imported modules.
        self._full_name_dict = {}
        #  Map the full module name to the alias and the module object (e.g. numpy.linalg to np)
        self.ignored_definitions = []
        # Objects of the module, that can not by sourced.
        # If there are any we can not reproduce the source.

        self.extract_definitions()


    def load_module(self, file_path: str) -> ModuleType:
        """
        Import the python module from the file. Create an empty module if the file doesn't exist.
        :param file:
        :return:
        """

        base = os.path.basename(file_path)
        base, ext = os.path.splitext(base)
        assert ext == ".py"
        with open(file_path, "r") as f:
            source = f.read()
        return self._load_from_source(name=base, source=source)


    def _load_from_source(self, name, source) -> ModuleType:
        """
        Create the _Module object from the source string 'source'.
        Should not be used.
        Named 'name'.
        """
        assert source, "Can not load empty source."
        new_module = imp.new_module(name)
        my_exec(source, new_module.__dict__, locals=None, description=name)
        return new_module


    def extract_definitions(self):
        """
        Extract definitions from the python module.
        :return:
        """
        analysis = []
        for name, obj in self.module.__dict__.items():
            # print(name, type(obj))
            if isinstance(obj, wrap.ActionWrapper):
                action = obj.action
                self.insert_definition(action)
                assert isinstance(action, action_base._ActionBase)
                assert name == action.name
                if action.is_analysis:
                    analysis.append(action)

            else:
                if type(obj) is ModuleType:
                    full_name = obj.__name__
                    self.imported_modules.append(obj)
                    self._full_name_dict[full_name] = name
                elif name[0] == '_':
                    self.ignored_definitions.append((name, obj))

        assert len(analysis) <= 1
        if analysis:
            # make instance of the main workflow
            analysis = analysis[0]
            self.analysis = ActionInstance.create(analysis)
        else:
            self.analysis = None


    def insert_definition(self, action: action_base._ActionBase, pos:int=None):
        """
        Insert a new definition of the 'action' to given position 'pos'.
        :param action: An action class (including dataclass construction actions).
        :param pos: Target position, default is __len__ meaning append to the list.
        :return:
        """
        if pos is None:
            pos = len(self.definitions)
        assert isinstance(action, action_base._ActionBase)
        self.definitions.insert(pos, action)
        self._name_to_def[action.name] = action




    @property
    def name(self):
        return self.module.__name__


    def code(self) -> str:
        """
        Generate the source code of the whole module.
        :return:
        """
        source = []
        # make imports
        for impr in self.imported_modules:
            full_name = impr.__name__
            alias = self._full_name_dict.get(full_name, None)
            if alias:
                import_line = "import {full} as {alias}".format(full=full_name, alias=alias)
            else:
                import_line = "import {full}".format(full=full_name)
            source.append(import_line)

        # make definitions
        for v in self.definitions:
            action = v
            source.extend(["", ""])     # two empty lines as separator
            source.append(action.code_of_definition(self._full_name_dict))
        return "\n".join(source)


    def save(self) -> None:
        assert not self.ignored_definitions
        with open(self.module_file, "w") as f:
            f.write(self.code())


    def update_imports(self):
        """
        Pass through all definition and collect all necessary imports.
        :return:
        TODO: ...
        """
        pass


    def get_analysis(self):
        """
        Return the list of analysis workflows of the module.
        :return:
        """
        analysis = [d for d in self.definitions if d.is_analysis]
        return analysis


    def get_workflow(self, name: str) -> wf._Workflow:
        """
        Get the workflow by the name.
        :param name:
        :return:
        """
        return self._name_to_def[name]

    def get_dataclass(self, name:str) -> Callable[..., data.DataClassBase]:
        dclass = self._name_to_def[name]
        return dclass._evaluate

"""
Object progression:
- Actions (implementation)

- Syntactic sugger classes
- ActionInstances - connection into WorkFlow
  This needs to be in close relation to previous since we want GUI - Python bidirectional conversions.
  
- Tasks - execution DAG
- Jobs
"""


"""
TODO:
1. first implement Class action with _name config parameter
2. Config parameters or impl. parameters - used to set some metadata of action.
3. Implement action decorator.
4. Implement evaluation mechanism - conversion to tasks, scheduler, evaluation of tasks by calling action evaluate methods.
5. Implement Evaluation class - keeping data from tasks and evaluation progress - close realtion to MJ, need concept of Resources.
"""
