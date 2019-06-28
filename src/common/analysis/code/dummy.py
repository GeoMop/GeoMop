from typing import *
from common.analysis import action_base as base
from common.analysis import action_base as base
from common.analysis import action_instance as instance
from common.analysis.converter import GetAttribute, GetItem
from common.analysis.action_instance import  ActionInstance


def is_underscored(s:Any) -> bool:
    return type(s) is str and s[0] == '_'


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


    def __init__(self, action: instance.ActionInstance) -> None:
        assert isinstance(action, instance.ActionInstance)
        self._action = action
        """Dummy pretend the data object of the action.output_type."""


    def __getattr__(self, key: str):
        # if key == '__action':
        #     return self.__dict__['__action']
        # TODO: update the type to know that it is a dataclass containing 'key'
        # TODO: check that type is dataclass
        assert not is_underscored(key)
        action = ActionInstance.create(GetAttribute(key), self._action)
        return Dummy.wrap(action)

    def __getitem__(self, idx: int):
        idx_wrap = ActionInstance.create(base.Value(idx))
        action = ActionInstance.create(GetItem(), self._action, idx_wrap)
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





