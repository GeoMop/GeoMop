"""Enums for ModelEditor.

.. codeauthor:: Tomas Krizek <tomas.krizek1@tul.cz>
"""

from enum import Enum


class PosType(Enum):
    comment = 1
    in_key = 2
    in_value = 3
    in_inner = 4


class KeyType(Enum):
    key = 1
    tag = 2
    ref = 3
    ref_a = 4
    anch = 5


class CursorType(Enum):
    key = 1
    tag = 2
    ref = 3
    anch = 4
    value = 5
    other = 6
    parent = 7

    @staticmethod
    def get_cursor_type(pos_type, key_type):
        """return type below cursor from PosType and KeyType"""
        if pos_type is PosType.in_key:
            if key_type is KeyType.key:
                return CursorType.key
            if key_type is KeyType.tag:
                return CursorType.tag
            if key_type is KeyType.anch:
                return CursorType.anch
            return CursorType.ref
        if pos_type is PosType.in_value:
            return CursorType.value
        return CursorType.other
