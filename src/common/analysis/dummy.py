from typing import *
from common.analysis import action_base as base
from common.analysis import converter


def is_underscored(s:Any) -> bool:
    return type(s) is str and s[0] == '_'


def separate_underscored_keys(arg_dict: Dict[str, Any]):
    underscored = {}
    regular = {}
    for key, value in arg_dict.items():
        if is_underscored(key):
            underscored[key] = value
        else:
            regular[key] = value
    return (regular, underscored)



class ActionWrapper:
    def __init__(self, action_class):
        assert issubclass(action_class, base._ActionBase)
        self.action_class = action_class
        self.is_analysis = False

    def __call__(self, *args, **kwargs):
        """
        Catch all arguments.
        Separate private params beginning with underscores.
        (Undummy action inputs, wrap non-action inputs)
        Create under laying action, connect to inputs.
        Return action wrapped into the Dummy.
        """
        regular_inputs, private_args = separate_underscored_keys(kwargs)
        action = self.action_class()
        remaining_args = action.set_inputs(input_list=args, input_dict=regular_inputs)
        # TODO: check that inputs are connected.
        if remaining_args:
            raise base.ExcUnknownArgument(remaining_args)
        action.set_metadata(private_args)
        return Dummy.wrap(action)



def public_action(action_class):
    """
    Decorator makes a wrapper function for an action that should be used explicitelty in workspace.
    A wrapper is called instead of the action constructor in order to:
    1. preprocess arguments
    2. return constructed action wrapped into the Dummy object.
    """
    return ActionWrapper(action_class)



class Dummy:
    """
    Dummy object for wrapping action as its output value.
    Absorbs all possible operations supported by the corresponding data type and convert then to
    appropriate implicit actions.
    """

    @classmethod
    def wrap(cls, action: Union['Dummy', base._ActionBase]):
        if isinstance(action, Dummy):
            return action
        else:
            return Dummy(action)


    def __init__(self, action: base._ActionBase):
        assert isinstance(action, base._ActionBase)
        self._action = action
        """Dummy pretend the data object of the action.output_type."""


    def __getattr__(self, key: str):
        # if key == '__action':
        #     return self.__dict__['__action']
        # TODO: update the type to know that it is a dataclass containing 'key'
        # TODO: check that type is dataclass
        assert not is_underscored(key)
        #action = object.__getattribute__(self, '__action').
        action = converter.GetAttribute.create(self._action, key)
        return Dummy.wrap(action)

    def __getitem__(self, idx: int):
        action = converter.GetItem.create(self._action, idx)
        return Dummy.wrap(action)

    # Binary
    # Operators
    #
    # Operator
    # Method
    # +                       object.__add__(self, other)
    # -                        object.__sub__(self, other)
    # *object.__mul__(self, other)
    # // object.__floordiv__(self, other)
    # / object.__div__(self, other)
    # % object.__mod__(self, other)
    # ** object.__pow__(self, other[, modulo])
    # << object.__lshift__(self, other)
    # >> object.__rshift__(self, other)
    # & object.__and__(self, other)
    # ^ object.__xor__(self, other)
    # | object.__or__(self, other)
    #
    # Assignment
    # Operators:
    #
    # Operator
    # Method
    # += object.__iadd__(self, other)
    # -= object.__isub__(self, other)
    # *= object.__imul__(self, other)
    # /= object.__idiv__(self, other)
    # //= object.__ifloordiv__(self, other)
    # %= object.__imod__(self, other)
    # **= object.__ipow__(self, other[, modulo])
    # <<= object.__ilshift__(self, other)
    # >>= object.__irshift__(self, other)
    # &= object.__iand__(self, other)
    # ^= object.__ixor__(self, other)
    # |= object.__ior__(self, other)
    #
    # Unary
    # Operators:
    #
    # Operator
    # Method
    # -                       object.__neg__(self)
    # +                      object.__pos__(self)
    # abs()
    # object.__abs__(self)
    # ~                      object.__invert__(self)
    # complex()
    # object.__complex__(self)
    # int()
    # object.__int__(self)
    # long()
    # object.__long__(self)
    # float()
    # object.__float__(self)
    # oct()
    # object.__oct__(self)
    # hex()
    # object.__hex__(self)
    #
    # Comparison
    # Operators
    #
    # Operator
    # Method
    # < object.__lt__(self, other)
    # <= object.__le__(self, other)
    # == object.__eq__(self, other)
    # != object.__ne__(self, other)
    # >= object.__ge__(self, other)
    # > object.__gt__(self, other)



