"""
Translation for lib package

Usage:
    In file declare::
    from langLib import gettext as _ 
"""
import gettext
import os

_d=os.path.dirname(os.path.realpath(__file__))
_t = gettext.translation('lib', _d+'/../locale')

def gettext(text):
    return _t.gettext(text)
