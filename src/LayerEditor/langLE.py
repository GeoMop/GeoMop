"""
Translation for LayerEditor package

Usage:
    In file declare::
    from langLE import gettext as _ 
"""
import gettext
import os

_d=os.path.dirname(os.path.realpath(__file__))
_t = gettext.translation('editor', _d+'/../locale', fallback=True)

def gettext(text):
    return _t.gettext(text)
