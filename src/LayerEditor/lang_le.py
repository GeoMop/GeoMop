# pylint: disable=C0103
"""
Translation for LayerEditor package

Usage:
    In file declare::
    from langLE import gettext as _
"""
import gettext as gt
import os

_d = os.path.dirname(os.path.realpath(__file__))
_t = gt.translation('editor', _d+'/../locale', fallback=True)

def gettext(text):
    """Translate to current lang"""
    return _t.gettext(text)
