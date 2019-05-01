import inspect
import indexed
import enum
import attr
import pytypes
import itertools
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





def closest_common_ancestor(a, b):
    cls_list = [a, b]
    mros = [reversed(inspect.getmro(cls)) for cls in cls_list]
    ancestor = None
    for ancestors in itertools.zip_longest(*mros):
        if len(set(ancestors)) == 1:
            ancestor = ancestors[0]
        else: break
    return ancestor






class ActionInputStatus(enum.IntEnum):
    missing = -1  # missing value
    error=-1    # type error
    none=0      # not checked yet
    seems_ok=1  # correct input, type not fully specified
    ok=2        # correct input

@attr.s(auto_attribs=True)
class ActionParameter:
    idx: int
    name: str
    type: Any =  None
    default: Any = None

    def get_default(self) -> Tuple[bool, Any]:
        if self.default:
            return True, self.default
        else:
            return False, self.default

def is_underscored(s:Any) -> bool:
    return type(s) is str and s[0] == '_'


@attr.s(auto_attribs=True)
class ActionArgument:
    parameter: ActionParameter
    value: '_ActionBase' = None
    is_default: bool = False
    status: ActionInputStatus = ActionInputStatus.missing


class _ActionBase:
    parameters : indexed.IndexedOrderedDict = []
    # Parameter specification list, class attribute, no parameters by default.
    output_type = None
    # Output type of the action, class attribute.
    # Both _parameters and _outputtype can be extracted from type annotations of the evaluate method using the _extract_input_type.

    @classmethod
    def _extract_input_type(cls):
        """
        Extract input and output types of the action from its evaluate method.
        Only support fixed numbeer of parameters named or positional.
        set: cls._input_type, cls._output_type
        """
        signature = inspect.signature(cls.evaluate)
        cls.parameters = indexed.IndexedOrderedDict()
        for i, param in enumerate(signature.parameters.values()):
            if param.name == 'self':
                continue
            assert param.kind  == param.POSITIONAL_ONLY or param.kind ==  param.POSITIONAL_OR_KEYWORD
            annotation = param.annotation if param.annotation != param.empty else None
            default = param.default if param.default != param.empty else None
            p = ActionParameter(i, param.name, annotation, default)
            cls.parameters[param.name]=p
        cls.output_type = signature.return_annotation

    """
    Single node of the DAG of a single Workflow.
    """
    def __init__(self, *args, **kwargs):
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
        """ Indicates the instance name provided by user."""
        self.output_actions = []
        """ Actions connected to the output. Set during the workflow construction."""
        self.arguments = []
        """ Inputs connected to the action parameters."""

        inputs = [(None, arg) for arg in args]
        inputs.extend(kwargs.items())
        remaining_args = self._reinit(inputs)
        if remaining_args:
            raise ExcUnknownArgument(remaining_args)

    @classmethod
    def action_name(cls) -> str:
        """
        Action name (not the instance name).
        :return:
        """
        return cls.__name__


    def name(self, instance_name: str) -> '_ActionBase':
        """
        Attribute setter. Usage:
        my_instance = SomeAction(inputs).name("instance_name")

        should be almost equivalent to:

        var.instance_name = SomeAction(inputs)

        :param instance_name:
        :return:
        """
        self.instance_name = instance_name
        self._proper_instance_name = True
        return self

    ParmeterItem = Tuple[Union[None, str], Any]
    RemainingArgs = Dict[Union[int, str], Any]
    def _reinit(self, inputs: Sequence[ParmeterItem]) -> RemainingArgs:
        """
        Reset action inputs and private arguments (underscore prefix).
        inputs: [ (arg_name, input) ]

        arg_name may be None in the case of positional arguments
        or valid parameter name.
        """

        # extract privte args, make dict of other args: name -> input
        self.private_args = {}
        input_args = {}
        for i, (name, input) in enumerate(inputs):
            if is_underscored(name):
                self.private_args[name] = input
            else:
                if name is None:
                    if i < len(self.parameters):
                        name = self.parameters[i].name
                    else:
                        name = i
                input_args[name] = input

        # fill and validate argument list
        self.arguments = []
        for param in self.parameters:
            is_default = False
            value = input_args.get(param.name, None)

            if value is None:
                is_default, value = param.get_default()
            else:
                del input_args[param.name]
            if value is None:
                self.arguments.append(ActionArgument(None, False, ActionInputStatus.missing))
                continue

            # check value
            try:
                value = _wrap_action(value)
            except ExcActionExpected:
                self.arguments.append(ActionArgument(None, is_default, ActionInputStatus.error_value))
                continue

            if not pytypes.is_subtype(value.output_type, param.type):
                self.arguments.append(ActionArgument(None, is_default, ActionInputStatus.error_type))
                continue
            self.arguments.append(ActionArgument(None, is_default, ActionInputStatus.seems_ok))

        # remaining arguments
        return input_args


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
            param, value, is_default, status = arg
            idx, name, type, default = param
            assert name
            assert isinstance(value, _ActionBase)
            inputs.append("{}={}".format(name, value.instance_name))

        input_string = ", ".join(inputs)
        if self._proper_instance_name:
            name = ".name(\"{}\")".format(self.instance_name)
        else:
            name = ""
        code_line =  "{} = wf.{}({}){}".format(self.instance_name, self.action_name(), input_string, name)
        return code_line

    def evaluate(self, inputs):
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


    def __getattribute__ (self, key):



def action(func):
    """
    Decorator to make an action class from the evaluate function.
    Action name is given by the nama of the function.
    Input types are given by the type hints of the function params.
    """
    action_name = func.__name__
    attributes = {
        "evaluate" : func,
    }
    action_class = type(action_name, (_ActionBase,), attributes)
    action_class._extract_input_type()
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
    base_types = [bool, int, float, complex, str, array]
    if isinstance(value, _ActionBase):
        return value
    elif type(value) in base_types:
        return converter._Value(value)
    elif type(value) is tuple:
        return converter.Tuple(*value)
    elif type(value) is list:
        return converter.List(*value)
    else:
        raise ExcActionExpected()