import os
import sys
import imp
import inspect
import traceback
import importlib
import typing

from common.analysis import action_base
from common.analysis import dummy








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



class _Module:
    """
    Object representing a module (whole file) that can contain
    several worflow and converter definitions and possibly also a script itself.

    We  inspect __dict__ of the loaded module to find all definitions.
    The script must be a workflow function decorated with @analysis decorator.

    Only functions under the @converter, @workflow, and @action decorators are
    captured, remaining code is ignored.
    """

    @staticmethod
    def create_from_source(name, source):
        """
        Create the _Module object from the source string 'source'.
        Named 'name'.
        """
        assert source, "Can not load empty source."
        new_module = imp.new_module(name)
        my_exec(source, new_module.__dict__, locals=None, description=name)
        return _Module(new_module)

    @staticmethod
    def create_from_file(file_path):
        """
        Create a _Module form the given file path.
        """
        base = os.path.basename(file_path)
        base, ext = os.path.splitext(base)
        assert ext == ".py"
        with open(file_path, "r") as f:
            source = f.read()
        return _Module.create_from_source(name=base, source=source)

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
        if not name or name[0] == '_':
            return False
        if isinstance(object, dummy.ActionWrapper):
            return True
        else:
            print('Ignored definition of: {}'.format(name))


    def __init__(self, module):
        """
        Constructor of the _Module wrapper.
        :param module: a python module object
        """
        self.module = module
        # Ref to wrapped python module object.
        self.definitions = {k:v for k, v in self.module.__dict__.items() if _Module.catch_object(k, v)}
        # List of analysis definition in the module (currently just defined workflows).
        self.analysis =  None
        # Instance of a workflow anotated by the decorator @analysis. Unique non-parametric workflow for running the analysis.

        for d in self.definitions.values():
            d.action_class.set_module("")

        analysis = [v for v in self.definitions.values() if v.is_analysis]
        assert len(analysis) <= 1
        if analysis:
            # make instance of the main workflow
            analysis = analysis[0]
            self.analysis = analysis()
        else:
            self.analysis = None

    @property
    def name(self):
        return self.module.__name__

    def code(self):
        source = ["import common.analysis as wf"]
        for v in self.definitions.values():
            action = v.action_class
            source.extend(["", ""])     # two empty lines as separator
            source.append(action.code())
        return "\n".join(source)




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
