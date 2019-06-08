import inspect
import indexed
import enum
import attr
import pytypes
from typing import *
from collections import defaultdict


# Name for the first parameter of the workflow definiton function that is used
# to capture instance names.
_VAR_="self"


class ExcMissingArgument(Exception):
    pass

class ExcActionExpected(Exception):
    pass

class ExcTooManyArguments(Exception):
    pass

class ExcUnknownArgument(Exception):
    pass

class ExcDuplicateArgument(Exception):
    pass



@attr.s(auto_attribs=True)
class ActionParameter:
    idx: int
    name: str
    type: Any = None
    default: Any = None

    def get_default(self) -> Tuple[bool, Any]:
        if self.default is not None:
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

    def is_variadic(self):
        return self._variable

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

        annotation = param.annotation if param.annotation != param.empty else None
        default = param.default if param.default != param.empty else None

        if param.kind == param.VAR_POSITIONAL:
            assert default == None
            param = ActionParameter(idx, None, annotation, default)
        else:
            assert param.kind == param.POSITIONAL_ONLY or param.kind == param.POSITIONAL_OR_KEYWORD, str(param.kind)
            param = ActionParameter(idx, param.name, annotation, default)
        parameters.append(param)
    return_type = signature.return_annotation
    return_type = return_type if return_type != signature.empty else None
    return parameters, return_type


class _ActionBase:

    """
    Base of all actions.
    - have defined parameters
    - have defined output type
    - implement expansion to the Task DAG.
    - have _code representation
    """
    def __init__(self, action_name = None ):
        self.is_analysis = False
        self.name = action_name or self.__class__.__name__
        self._module = "wf"
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
        pass



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


    def format(self, n_args=None):
        """
        Return a format string for the expression that constructs the action.
        :param n_args: Number of arguments, number of placeholders. Can be None if the action is not variadic.
        :return: str, format
        Format contains '{N}' placeholders for the given N-th argument, the named placeholer '{VAR}'
        is used for the variadic arguments, these are substituted as an argument list separated by comma and space.
        E.g. "Action({0}, {1}, {})" can be expanded to :
        "Action(arg0, arg1, arg2, arg3)"
        """
        if n_args is None:
            assert not self.parameters.is_variadic()
            n_args = self.parameters.size()
        assert n_args >= self.parameters.size()
        args=[]
        for i_arg in range(n_args):
            param = self.parameters.get_index(i_arg)
            if param.name:
                args.append("{name}={{{idx}}}".format(name=param.name, idx=i_arg))
            else:
                args.append("{{{idx}}}".format(idx=i_arg))
        args = ", ".join(args)

        module_str = self._module
        if module_str:
            action_name = "{}.{}".format(module_str, self.name)
        else:
            action_name = self.name

        return "{{action_name}}({args})".format(args=args)


    def validate(self, inputs):
        return self.evaluate(inputs)


    def expand(self):
        pass


    def set_module(self, module_name):
        if module_name != '__main__':
            self._module = module_name


class Value(_ActionBase):
    def __init__(self, value):
        super().__init__()
        self.value = value

    def evaluate(self, arguments):
        return self.value

    def format(self, n_args):
        value = self.value
        if type(value) is str:
            expr = "'{}'".format(value)
        else:
            expr = str(value)
        return expr





class _ListBase(_ActionBase):

    # We assume that parameters are used only in reinit, which do not use it
    # in this case. After reinit one should use only self.arguments.

    def __init__(self):
        super().__init__()
        self.parameters = Parameters()
        self.parameters.append(ActionParameter(idx=0, name=None, type=Any, default=None))


# class Tuple(_ListBase):
#     #__action_parameters = [('input', 'Any')]
#     """ Merge any number of parameters into tuple."""
#     def _code(self):
#         return self._code_with_brackets(format = "({})")
#
#     def evaluate(self, inputs):
#         return tuple(inputs)


class List(_ListBase):

    def format(self, n_args):
        assert n_args is not None
        args=["{{{idx}}}".format(idx=i_arg) for i_arg in range(n_args)]
        args = ", ".join(args)
        return "[{args}]".format(args=args)

    def evaluate(self, inputs):
        return list(inputs)





class ClassActionBase(_ActionBase):
    """
    Dataclass action
    """
    def __init__(self, data_class):
        super().__init__(data_class.__name__)
        self._data_class = data_class
        self._module = ""
        self._extract_input_type(func=data_class.__init__, skip_self=True)


    @staticmethod
    def construct_from_params(name: str, params: Parameters):
        """
        Use Params to consturct the data_class and then instance of ClassActionBase.
        :param name:
        :param params:
        :return:
        """
        attributes = {}
        for param in params:
            attributes[param.name] = attr.ib(default=param.default, type=param.type)
        data_class = type(name, (object,), attributes)
        data_class = attr.s(data_class)
        return ClassActionBase(data_class)

    def _evaluate(self, *args):
        return self._data_class(*args)


    def code_of_definition(self, module_name_dict):
        lines = ['@wf.Class']
        lines.append('class {}:'.format(self.name))
        for attribute in self._data_class.__attrs_attrs__:
            type_str = attribute.type.__name__ if attribute.type else "Any"
            if attribute.default == attr.NOTHING:
                default = ""
            else:
                default = "={}".format(attribute.default)
            lines.append("    {}:{}{}".format(attribute.name, type_str, default))

        return "\n".join(lines)
