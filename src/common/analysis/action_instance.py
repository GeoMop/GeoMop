import pytypes
import enum
import attr
from typing import List, Dict, Union
from numpy import array

from common.analysis import action_base as base






class ActionInputStatus(enum.IntEnum):
    missing     = -3     # missing value
    error_value = -2     # error input passed, can not be wrapped into an action
    error_type  = -1     # type error
    none        = 0      # not checked yet
    seems_ok    = 1      # correct input, type not fully specified
    ok          = 2      # correct input


@attr.s(auto_attribs=True)
class ActionArgument:
    parameter: base.ActionParameter
    value: 'base._ActionBase' = None
    is_default: bool = False
    status: ActionInputStatus = ActionInputStatus.missing

InputDict = Dict[str, '_ActionBase']
InputList = List['_ActionBase']
RemainingArgs = Dict[Union[int, str], '_ActionBase']



class ActionInstance:
    """
    A building block of the workflow. Vertex of its (unexpanded) DAG.

    """
    def __init__(self, action : base._ActionBase, name : str = None) -> None:
        self.name = name
        """ The instance name. (i.e. name of variable containing this instance.)"""
        self._proper_instance_name = False
        """ Indicates the instance name provided by user. Not generic name."""

        self.action = action
        """ The Action (instance of _ActionBase), have defined parameter. """
        self.arguments: List[ActionArgument] = []
        self._fill_args()
        """ Inputs connected to the action parameters."""
        self.output_actions = []
        """ Actions connected to the output. Set during the workflow construction."""


    def _fill_args(self):
        """
        Fill unset arguments.
        :return:
        """
        while True:
            param = self.parameters.get_index(len(self.arguments))
            if param is None or param.name is None:
                break
            self.arguments.append(self.make_argument(param, None))


    @staticmethod
    def create(action, *args, **kwargs):
        """
        Create an action instance with given arguments.
        :param args:
        :param kwargs:
        :return:
        """
        assert isinstance(action, base._ActionBase)
        instance = ActionInstance(action)
        remaining_args, duplicate = instance.set_inputs(input_list=args, input_dict=kwargs)
        if remaining_args:
            raise base.ExcUnknownArgument(remaining_args)
        if duplicate:
            raise base.ExcDuplicateArgument(duplicate)

        return instance


    @property
    def parameters(self):
        return self.action.parameters

    @property
    def output_type(self):
        return self.action.output_type

    @property
    def action_name(self):
        return self.action.name

    def make_argument(self, param, value):

        is_default = False
        if value is None:
            is_default, value = param.get_default()
            if is_default:
                value = ActionInstance.create(base.Value(value))

        if value is None:
            return ActionArgument(param, None, False, ActionInputStatus.missing)

        # if not isinstance(value, ActionInstance):
        #     x = 1
        assert isinstance(value, ActionInstance), type(value)
        if not pytypes.is_subtype(value.output_type, param.type):
            return  ActionArgument(param, value, is_default, ActionInputStatus.error_type)

        return ActionArgument(param, value, is_default, ActionInputStatus.seems_ok)


    def set_inputs(self, input_list: InputList = [], input_dict: InputDict={}) -> RemainingArgs:
        """
        Set inputs of an explicit action with fixed number of named parameters.
        input_list: [ input ]  positional arguments.
        input_dict: { parameter_name: input } named arguments
        """
        params = self.parameters
        old_args = self.arguments
        self.arguments = []

        # Process all positional arguments.
        for i_arg, arg in enumerate(input_list):
            param = params.get_index(i_arg)
            self.arguments.append(self.make_argument(param, arg))

        len_args = len(self.arguments)
        self._fill_args()
        # Fill remaining arguments
        for i_param in range(len_args, self.parameters.size()):
            param = self.parameters.get_index(i_param)
            if param.name is None:
                break
            old_arg = old_args[param.idx]
            value = input_dict.get(param.name, old_arg.value)
            self.arguments[i_param] = self.make_argument(param, value)

        # Set named arguments
        unknown_args = {}
        duplicate_args = {}
        for key, val in input_dict.items():
            param = self.parameters.get_name(key)
            if param is None:
                unknown_args[key] = val
            else:
                if param.idx < len(input_list):
                    duplicate_args[key] = val

        return unknown_args, duplicate_args


    def set_single_input(self, idx, value):
        """
        API fro GUI
        :param idx: Index of argument to set, if None try to add
        input in the case of variadic parameters.
        :param value: value or action to set for the input, or None to unset the input.
        """
        if idx is None:
            idx = len(self.arguments)
        param = self.parameters.get_index(idx)
        assert param is not None
        if idx == len(self.arguments):
            self.arguments.append(self.make_argument(param, None))
        self.arguments[idx] = self.make_argument(param, value)

        # remove empty variadic inputs
        while self.arguments and self.arguments[-1].status == ActionInputStatus.missing \
              and self.arguments[-1].parameter.name is None:
            self.arguments.pop(-1)


    def set_name(self, instance_name: str):
        """
        Set name of the action instance. Used for code representation
        to name the variable.
        """
        self.name = instance_name
        self._proper_instance_name = True
        return self


    def get_code_instance_name(self):
        if self._proper_instance_name:
            return "{}.{}".format(base._VAR_, self.name)
        else:
            return self.name





    def relative_action_name(self, module_dict):
        """
        Construct the action class name for given set of imported modules.
        :param module_dict: A dict mapping the full module path to its imported alias.
        :return: The action name using the alias instead of the full module path.
        """
        action_name = self.action_name
        action_module = self.action.__module__
        alias = module_dict.get(action_module)
        if alias:
            return "{}.{}".format(alias, action_name)
        else:
            return action_name


    def code(self, module_dict):
        """
        Return a representation of the action instance.
        This is generic representation code that calls the constructor.

        Two

        :param inputs: Dictionary assigning strings to the Action's parameters.
        :param config: String used for configuration, call serialization of the configuration by default.
        :return: string (code to instantiate the action)
        """
        expr_format = self.action.format(len(self.arguments))
        inputs = [arg.value.get_code_instance_name() for arg in self.arguments]
        expression = expr_format.format(*inputs, action_name=self.relative_action_name(module_dict))
        code_line =  "{} = {}".format(self.get_code_instance_name(), expression)
        return code_line
