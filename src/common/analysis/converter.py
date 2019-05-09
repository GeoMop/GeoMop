
import indexed
from typing import *
from common.analysis import types
from common.analysis import action_base as base

"""
Mechanism for parsing the Python code into the DAG of action for
a single workflow. Contains actions that are not meant to be 
used directly.
"""



class Value(base._ActionBase):
    def __init__(self, value):
        super().__init__()
        self.value = value

    def evaluate(self, inputs):
        return self.value

    def _code(self):
        value = self.value
        if type(value) is str:
            value = "'{}'".format(value)
        else:
            value = str(value)

        code_line = "{} = {}".format(self.get_code_instance_name(), value)
        return code_line





class _ListBase(base._ActionBase):

    # We assume that parameters are used only in reinit, which do not use it
    # in this case. After reinit one should use only self.arguments.

    def __init__(self, *inputs):
        self.parameters = []
        super().__init__()
        self.set_inputs(input_list=list(inputs))

    InputDict = Dict[str, base._ActionBase]
    InputList = List[base._ActionBase]
    RemainingArgs = Dict[Union[int, str], base._ActionBase]

    def set_inputs(self, input_dict: InputDict={}, input_list: InputList = []) -> RemainingArgs:
        """
        Set inputs of an action with variable number of parameters (Tuple, List).
        Unlike _ActionBase.set_inputs, the arguments list is completely overwritten.
        :param input_dict: must be empty
        :param input_list:
        """
        assert len(input_dict) == 0
        self.arguments = []
        common_type = None
        parameter = base.ActionParameter(idx=None, name="", type=Any, default=None)
        for arg in input_list:
            value = base._wrap_action(arg)
            value_type = value.output_type
            if common_type is None:
                common_type = value_type
            else:
                common_type = base.closest_common_ancestor(common_type, value_type)
            arg = base.ActionArgument(parameter, value, False, base.ActionInputStatus.none)
            self.arguments.append(arg)
        #parameter.type = common_type
        #self.output_type = type.Tuple(common_type)
        return {}

    def _code_with_brackets(self, format: str):
        inputs=[]
        for arg in self.arguments:
            assert isinstance(arg.value, base._ActionBase)
            inputs.append(arg.value.get_code_instance_name())

        input_string = ", ".join(inputs)
        rhs = format.format(input_string)
        code_line = "{} = {}".format(self.get_code_instance_name(), rhs)
        return code_line



# class Tuple(_ListBase):
#     #__action_parameters = [('input', 'Any')]
#     """ Merge any number of parameters into tuple."""
#     def _code(self):
#         return self._code_with_brackets(format = "({})")
#
#     def evaluate(self, inputs):
#         return tuple(inputs)


class List(_ListBase):
    def _code(self):
        return self._code_with_brackets(format = "[{}]")

    def evaluate(self, inputs):
        return list(inputs)




class GetAttribute(base._ActionBase):


    def _code(self):
        data_class = self.arguments[0].value
        assert isinstance(data_class, base._ActionBase)
        attr_name = self.arguments[1].value
        assert isinstance(attr_name, Value)
        attr_name = attr_name.evaluate([])
        return "{} = {}.{}".format(self.get_code_instance_name(), data_class.get_code_instance_name(), attr_name)

    @staticmethod
    def _evaluate(data_class: Any, attr_name: str):
        return data_class.get_attribute(attr_name)

GetAttribute._extract_input_type()



@base.action
def GetItem(data_list, idx: str):
    return data_list[idx]



