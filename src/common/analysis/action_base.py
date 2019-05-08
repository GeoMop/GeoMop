import inspect
import indexed
import enum
import attr
import pytypes
from numpy import array
from typing import *
from collections import defaultdict

class ExcMissingArgument(Exception):
    pass

class ExcActionExpected(Exception):
    pass

class ExcTooManyArguments(Exception):
    pass

class ExcUnknownArgument(Exception):
    pass



_VAR_="self"


class ActionInputStatus(enum.IntEnum):
    missing     = -3     # missing value
    error_value = -2     # error input passed
    error_type  = -1     # type error
    none        = 0      # not checked yet
    seems_ok    = 1      # correct input, type not fully specified
    ok          = 2      # correct input

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


@attr.s(auto_attribs=True)
class ActionArgument:
    parameter: ActionParameter
    value: '_ActionBase' = None
    is_default: bool = False
    status: ActionInputStatus = ActionInputStatus.missing


class _ActionBase:
    parameters = indexed.IndexedOrderedDict()
    # Parameter specification list, class attribute, no parameters by default.
    output_type = None
    # Output type of the action, class attribute.
    # Both _parameters and _outputtype can be extracted from type annotations of the evaluate method using the _extract_input_type.
    _module = "wf"

    @classmethod
    def _extract_input_type(cls, func=None, skip_self=False):
        """
        Extract input and output types of the action from its evaluate method.
        Only support fixed numbeer of parameters named or positional.
        set: cls._input_type, cls._output_type
        """
        if func is None:
            func = cls._evaluate
        signature = inspect.signature(func)
        parameters = indexed.IndexedOrderedDict()

        for param in signature.parameters.values():
            idx = len(parameters)
            if skip_self and idx==0 and param.name == 'self':
                continue
            assert param.kind  == param.POSITIONAL_ONLY or param.kind ==  param.POSITIONAL_OR_KEYWORD
            annotation = param.annotation if param.annotation != param.empty else None
            default = param.default if param.default != param.empty else None

            p = ActionParameter(idx, param.name, annotation, default)
            parameters[param.name]=p
        cls.parameters = parameters
        cls.output_type = signature.return_annotation


    @classmethod
    def create(cls, *args, **kwargs):
        c = cls()
        c.set_inputs(input_list=args, input_dict=kwargs)
        return c


    """
    Single node of the DAG of a single Workflow.
    """
    def __init__(self):
        """
        Catch all arguments, separate private params beginning with underscores.
        Extract parameters according to input_type(), store input actions in proper order into
        self._inputs.

        :param args:
        :param kwargs:
        """
        self.instance_name = None
        """ Unique ID within the workspace. Checked and updated during the workspace construction."""
        self._proper_instance_name = False
        """ Indicates the instance name provided by user. Not generic name."""
        self.output_actions = []
        """ Actions connected to the output. Set during the workflow construction."""
        self.arguments = [ActionArgument(param, None, False, ActionInputStatus.missing) for param in self.parameters]
        """ Inputs connected to the action parameters."""


    @classmethod
    def action_name(cls) -> str:
        """
        Action name (not the instance name).
        :return:
        """
        return cls.__name__

    @classmethod
    def set_module(cls, module_name):
        if module_name != '__main__':
            cls._module = module_name

    def set_name(self, instance_name: str):
        """
        Set name of the action instance. Used for code representation
        to name the variable.
        """
        self.instance_name = instance_name
        self._proper_instance_name = True
        return self



    InputDict = Dict[str, '_ActionBase']
    InputList = List['_ActionBase']
    RemainingArgs = Dict[Union[int, str], '_ActionBase']

    def set_inputs(self, input_dict: InputDict={}, input_list: InputList = []) -> RemainingArgs:
        """
        Set inputs of an explicit action with fixed number of named parameters.
        input_dict: { parameter_name: input }
        input_list: [ input ]  used only in List and Tuple actions.
        ... see their set_inputs method.
        """

        # Process positional parameters. DEPRECATED.
        for i, input in enumerate(input_list):
            if i < len(self.parameters):
                name = self.parameters.values()[i].name
            else:
                name = i
            input_dict[name] = input

        # fill and validate argument list
        for param in self.parameters.values():
            old_arg = self.arguments[param.idx]
            value = input_dict.get(param.name, old_arg.value)

            is_default = False
            if value is None:
                is_default, value = param.get_default()
            else:
                input_dict.pop(param.name, None)    # safe remove

            if value is None:
                self.arguments[param.idx] = ActionArgument(param, None, False, ActionInputStatus.missing)
                continue


            try:
                value = _wrap_action(value)
            except ExcActionExpected:
                self.arguments[param.idx] = ActionArgument(param, None, is_default, ActionInputStatus.error_value)
                continue

            if not pytypes.is_subtype(value.output_type, param.type):
               self.arguments[param.idx] = ActionArgument(param, value, is_default, ActionInputStatus.error_type)
               continue

            self.arguments[param.idx] = ActionArgument(param, value, is_default, ActionInputStatus.seems_ok)

        # remaining arguments
        return input_dict


    def set_metadata(self, metadata: InputDict={}):
        pass

    def get_code_instance_name(self):
        if self._proper_instance_name:
            return "{}.{}".format(_VAR_, self.instance_name)
        else:
            return self.instance_name

    def _code(self):
        """
        Return a representation of the action instance.
        This is generic representation code that calls the constructor.

        Two

        :param inputs: Dictionary assigning strings to the Action's parameters.
        :param config: String used for configuration, call serialization of the configuration by default.
        :return: string (code to instantiate the action)
        """
        inputs=[]
        for arg in self.arguments:
            assert isinstance(arg.value, _ActionBase)
            input_instance = arg.value.get_code_instance_name()
            inputs.append("{}={}".format(arg.parameter.name, input_instance))

        input_string = ", ".join(inputs)
        module_str = self._module
        if module_str:
            action_name = "{}.{}".format(module_str, self.action_name())
        else:
            action_name = self.action_name()
        code_line =  "{} = {}({})".format(self.get_code_instance_name(), action_name, input_string)
        return code_line

    def evaluate(self, inputs):
        inputs = {arg.param.name: input for arg, input in zip(self.arguments, inputs)}
        return self._evaluate(**inputs)

    @staticmethod
    def _evaluate():
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




def action(func):
    """
    Decorator to make an action class from the evaluate function.
    Action name is given by the nama of the function.
    Input types are given by the type hints of the function params.
    """
    action_name = func.__name__
    attributes = {
        "_evaluate": func,
    }
    action_class = type(action_name, (_ActionBase,), attributes)
    action_class._extract_input_type(func=func)
    return action_class





def _wrap_action(value):
    """
    Try to wrap given value into generic action. Works for:
    - base types: bool, int, float, str, numpy.array, ... -> wrap into auxiliary _Value action
    - tuple -> Tuple action
    - list -> List action
    :param value:
    :return:
    """
    import common.analysis.converter as converter
    import common.analysis.dummy as dummy

    if isinstance(value, dummy.Dummy):
        value = value._action

    base_types = [bool, int, float, complex, str, array]
    if isinstance(value, _ActionBase):
        return value
    elif type(value) in base_types:
        return converter.Value(value)
    elif type(value) is tuple:
        #TODO: Warning
        return converter.List(*value)
    elif type(value) is list:
        return converter.List(*value)
    else:
        raise ExcActionExpected("Have value: {}".format(str(value)))