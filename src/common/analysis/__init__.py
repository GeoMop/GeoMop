from common.analysis.code.decorators import workflow, analysis, action, Class
from .action import *

"""
# Minimalistic implementation of the analysis data layer for the GUI.

TODO:
1. Improved code generation:
    - modify _code methods to return (instance_name, format, list of instance to substitute into the format)
    - modify workspace code to dynamicaly expand format to obtain not extremaly long code representation:
        try to expand:
            - Value, dataclass instance, Tuple, List, GetAttribute ... should be the action property

2. Separate Action and ActionInstance
    - Instances of Action class are just distinct actions, need not to create classes dynamicaly.
      e.g. instances of Workflow would be just different workflow definitions, like function definitions.
    - Similarly dataclass constructors would be just instances of the DataClass action.
    - Common actions would be just instances of the Action class providing the evaluation function as the parameter
      and possibly some metadata. 

3. Make workflows, dataclasses, enums accessible by import

3. Can use dataclasses both as constructors and as type specification 
   (must set a _type attribute to the action wrapper function)

3. user modules: 
    - from analysis.workflow import *
        - decorators: workflow, analysis, Class, Enum
        - actions - basic, other in modules, lowercase
        - types - basic, other in modules, UpperCase 
    
    - from analysis import impl
        - @impl.action
        - impl.ActionBase
        - impl.AtomicAction
        - impl.DynamicAction  
    
    - Module
      [ Workflow, Class, Enum, Analysis]
    - Workflow
      [ ActionInstance ]
    - ActionInstance
      [ ActionBase ]
    code, workflow_dag, task_dag, scheduler
    
3. Refactor codebase ??:
    - 
    - module to import in GUI (
    - module to import in Action sources ( decorators, types)
    - separate code for creating the analysis from the Python representation (dummy etc.)
    - GUI api
    - code for base action classes
      
4. Simplest evaluation support.
    - create Task DAG from the root analysis workflow.
    - process the Task DAG (serialy directly in Python)

5. Safe loading of sources in separate process.
    - Load and safe in separate process, catching the errors and prevent crashes and infinite loops.
    - Load the round trip source in the GUI/evaluation 
    
6. Typechecking

- have common class for actions (current classes)
- other class (composition) for action instance
  ... no dynamical class creation
- How to deal with types, i.e. with dataclasses ... thats fine current spec have no support for inheritance
"""


