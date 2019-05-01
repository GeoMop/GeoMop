"""
Functions:

- Make action input specification from its parameter annotation.
- Inspect type specification (from GUI).
- Validate data against type.

"""

import attr
from common.analysis import converter


# class Type:
#     pass
#
# class List:
#     def __init__(self, item_type):
#         self.item_type = item_type




def Class(data_class):
    """
    Decorator to add dunder methods using attr.
    Moreover dot access returns the converter.Get action instead of the value itself.
    This is necessary to catch it in the workflow decorator.
    """
    data_class = attr.s(data_class)
    data_class.get_attribute = data_class.__getattribute__
    data_class.__getattribute__ = lambda self, name: converter.Get(self, name)
    return data_class