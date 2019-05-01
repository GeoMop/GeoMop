from common.analysis import action_base as base
import indexed
from typing import *


class _Value(base._ActionBase):
    def __init__(self, value):
        super().__init__()
        self.value = value

    def evaluate(self, inputs):
        return self.value

    def _code(self):
        return str(self.value)

class _ListBase(base._ActionBase):
    parameters: indexed.IndexedOrderedDict = []
    # We assume that parameters are used only in reinit, which do not use it
    # in this case. After reinit one should use only self.arguments.

    def __init__(self, *inputs):
        super().__init__(*inputs)
    # TODO: reinit with variable number of arguments---


    def _reinit(self, inputs: Sequence[base._ActionBase.ParmeterItem]) -> base._ActionBase.RemainingArgs:
        self.arguments = []
        common_type = None
        parameter = base.ActionParameter(None,"", None, None)
        for name, arg in inputs:
            assert name is None
            value = base._wrap_action(arg)
            value_type = value.output_type
            if common_type is None:
                common_type = value_type
            else:
                common_type = base.closest_common_ancestor(common_type, value_type)
            arg = base.ActionArgument(parameter, value, False, base.ActionInputStatus.none)
            self.arguments.append(arg)
        return {}

    def _code_with_backets(self, format: str):
        inputs=[]
        for arg in self.arguments:
            param, value, is_default, status = arg
            assert isinstance(value, base._ActionBase)
            inputs.append(value.instance_name)

        input_string = ", ".join(inputs)
        rhs = format.format(input_string)
        if self._proper_instance_name:
            code_line = "self.{} = {}".format(self.instance_name, rhs)
        else:
            code_line = "{} = {}".format(self.instance_name, rhs)
        return code_line



class Tuple(_ListBase):
    #__action_parameters = [('input', 'Any')]
    """ Merge any number of parameters into tuple."""
    def _code(self):
        return self._code_with_brackets(format = "({})")

    def evaluate(self, inputs):
        return tuple(inputs)


class List(_ListBase):
    def _code(self):
        return self._code_with_brackets(format = "[{}]")

    def evaluate(self, inputs):
        return list(inputs)


@base.action
def Get(self, data_class, attr_name: str):
    data_class, attr_name = inputs
    return data_class.get_attribute(attr_name)


class Class(base._ActionBase):
    def __init__(self, data_class, **kwargs):
        self.data_class = data_class
        super().__init__(**kwargs)

    def evaluate(self, inputs):
        inputs = {name:input for name, input in zip(self.arg_names, inputs)}
        self.data_class(**inputs)



    # name = kwargs.get("_name", None)
    # parameters = {k:v for k, v in kwargs.items() if k[0] != "_"}
    # data_class = attr.make_class(name, parameters.keys())
    # data_instance = data_class(**parameters)
    # return data_instance

