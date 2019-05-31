import inspect
import indexed
import enum
import attr
import pytypes
from typing import *
from collections import defaultdict








@attr.s(auto_attribs=True)
class ActionParameter:
    idx: int
    name: str
    type: Any = None
    default: Any = None

    def get_default(self) -> Tuple[bool, Any]:
        if self.default:
            return True, self.default
        else:
            return False, self.default


class Parameters:
    def __init__(self):
        self.parameters = []
        # List of Action Parameters
        self._name_dict = {}
        # Map names to parameters.
        self._variable = False
        # indicates variable number of parameters, the last param have None name

    def size(self):
        return len(self.parameters)

    def append(self, param : ActionParameter):
        assert not self._variable, "Duplicate definition of variadic parameter."
        if param.name is None:
            self._variable = True
        else:
            assert param.name not in self._name_dict
            self._name_dict[param.name] = param
        self.parameters.append(param)


    def get_name(self, name):
        return self._name_dict.get(name, None)


    def get_index(self, idx):
        if idx >= len(self.parameters):
            if self._variable:
                return self.parameters[-1]
            else:
                return None
        return self.parameters[idx]


    def __iter__(self):
        return iter(self.parameters)


def extract_func_signature(func, skip_self=True):
    """
    Inspect function signature and extract parameters, their types and return type.
    :param func: Function to inspect.
    :param skip_self: Skip first parameter if its name is 'self'.
    :return:
    """
    signature = inspect.signature(func)
    parameters = Parameters()

    for param in signature.parameters.values():
        idx = parameters.size()
        if skip_self and idx == 0 and param.name == 'self':
            continue
        assert param.kind == param.POSITIONAL_ONLY or param.kind == param.POSITIONAL_OR_KEYWORD, str(param.kind)
        annotation = param.annotation if param.annotation != param.empty else None
        default = param.default if param.default != param.empty else None

        param = ActionParameter(idx, param.name, annotation, default)
        parameters.append(param)
    return parameters, signature.return_annotation


class _ActionBase:
    _module = "wf"

    """
    Base of all actions.
    - have defined parameters
    - have defined output type
    - implement expansion to the Task DAG.
    - have _code representation
    """
    def __init__(self, action_name = None ):
        self.name = action_name or self.__class__.__name__

        self.parameters = Parameters()
        # Parameter specification list, class attribute, no parameters by default.
        self.output_type = None
        # Output type of the action, class attribute.
        # Both _parameters and _outputtype can be extracted from type annotations of the evaluate method using the _extract_input_type.
        self._extract_input_type()

    def _extract_input_type(self, func=None, skip_self=True):
        """
        Extract input and output types of the action from its evaluate method.
        Only support fixed numbeer of parameters named or positional.
        set: cls._input_type, cls._output_type
        """
        if func is None:
            func = self._evaluate
        self.parameters, self.output_type = extract_func_signature(func, skip_self)



    # def evaluate(self, inputs):
    #     inputs = {arg.param.name: input for arg, input in zip(self.arguments, inputs)}
    #     return self._evaluate(**inputs)


    def _evaluate(self):
        """
        Pure virtual method.
        If the validate method is defined it is used for type compatibility validation otherwise
        this method must handle both a type tree and the data tree on the input
        returning the appropriate output type tree or the data tree respectively.
        :param inputs: List of actual inputs. Same order as the action arguments.
        :return:
        """
        assert False, "Implementation has to be provided."



    def validate(self, inputs):
        return self.evaluate(inputs)


    def expand(self):
        pass




class Value(_ActionBase):
    def __init__(self, value):
        super().__init__()
        self.value = value

    def evaluate(self, arguments):
        return self.value

    def _code(self):
        value = self.value
        if type(value) is str:
            value = "'{}'".format(value)
        else:
            value = str(value)

        code_line = "{} = {}".format(self.get_code_instance_name(), value)
        return code_line





class _ListBase(_ActionBase):

    # We assume that parameters are used only in reinit, which do not use it
    # in this case. After reinit one should use only self.arguments.

    def __init__(self):
        super().__init__()
        self.parameters = Parameters()
        self.parameters.append(ActionParameter(idx=0, name=None, type=Any, default=None))


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





class ClassActionBase(_ActionBase):
    """
    Dataclass action
    """
    def __init__(self, data_class):
        super().__init__()
        self._data_class = data_class
        self._module = ""
        self._extract_input_type(func=data_class.__init__, skip_self=True)

    def _evaluate(self, **kwargs):
        return self._data_class(**kwargs)


    def code(self):
        lines = ['@wf.Class']
        lines.append('class {}:'.format(self.action_name()))
        for attribute in self._data_class.__attrs_attrs__:
            type_str = attribute.type.__name__ if attribute.type else "Any"
            if attribute.default == attr.NOTHING:
                default = ""
            else:
                default = "={}".format(attribute.default)
            lines.append("  {}:{}{}".format(attribute.name, type_str, default))

        return "\n".join(lines)
