from common.analysis.code.decorators import workflow, analysis, action, Class
from .action import *

"""
# Minimalistic implementation of the analysis data layer for the GUI.

GUI TODO:
- changes (name, slots, result type) in workflow may break workflow that use it
- ? change slot and result types automaticaly or explicitely (that


TODO:
0. DFS - add detection of cycle    
    
1. GUI API for adding and removing definitions from module
2. GUI way to create and modify the workflow, in particular update a workflow from slots and result.
3. GUI way to modify dataclasses and enums

3. test importing of user modules, better test of module functions
    - every action knows its __module__ that is full module name (not the alias from the import) 
    - must pass imports as a dictionalry to translate full module names to aliasses
    - implement full and iterative collection of used modules in definitions of the module
    #instance should  know its module path 
4. test_gui_api, etc.

1. Improved code generation:
    - modify _code methods to return (instance_name, format, list of instance to substitute into the format)
    - modify workspace code to dynamicaly expand format to obtain not extremaly long code representation:
        try to expand:
            - Value, dataclass instance, Tuple, List, GetAttribute ... should be the action property

4. Simplest evaluation support.
    - create Task DAG from the root analysis workflow.
    - process the Task DAG (serialy directly in Python)


    
      

6. Typechecking

- have common class for actions (current classes)
- other class (composition) for action instance
  ... no dynamical class creation
- How to deal with types, i.e. with dataclasses ... thats fine current spec have no support for inheritance
- Need typing extension to specify protocol "a dataclass with a key xyz"
- Can use dataclasses both as constructors and as type specification 
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


0: base actions overview
    data manipulation:
    - Value
    - Class ..
    - List
    - Dict
    - GetAttribute
    - GetListItem
    - GetDictItem
    
    ?? transpose - List[Class] -> Class[List] etc.
    ... sort of 'zip'
    
    expressions:
    - operators: +, -, *, /, %, **, @, 
    - math functions
    - not able to capture parenthesis
    
    file: 
    - load/save YAML/JSON + template substitution
    - serialization/deserialization of dataclasses and whole datatrees
    
    
    metaactions (actions taking a workflow as parameter):
    - foreach - apply a workflow with single slot to every item of a list 
    - while - takes the BODY workflow (automorphism) and PREDICATE (bool result)
            - expand BODY only if PREDICATE is true. 


5. Safe loading of sources in separate process.
    - Load and safe in separate process, catching the errors and prevent crashes and infinite loops.
    - Load the round trip source in the GUI/evaluation 
    
"""


