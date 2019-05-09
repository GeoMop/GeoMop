from .workflow import workflow, analysis, Class
from .action import *

"""
TODO:
- modify _code methods to return (instance_name, format, list of instance to substitute into the format)
- modify workspace code to dynamicaly expand format to obtain not extremaly long code representation:
  try to expand:
    - Value, dataclass instance, Tuple, List, GetAttribute ... should be the action property
- have common class for actions (current classes)
- other class (composition) for action instance
  ... no dynamical class creation
- How to deal with types, i.e. with dataclasses ... thats fine current spec have no support for inheritance
"""
