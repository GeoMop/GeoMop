"""
Module contains helper functions for loading stylesheets.
"""

__author__ = 'Tomas Krizek'

import os

# TODO: move resources folder
__stylesheet_dir__ = os.path.join(
    os.path.split(os.path.dirname(os.path.realpath(__file__)))[0],
    "..", 'lib', 'resources', 'css') + os.path.sep


def load_stylesheet(name):
    """Loads the stylesheet file to a string."""
    if not name.endswith('.css'):
        name += '.css'

    path = __stylesheet_dir__ + name
    if os.path.isfile(path):
        with open(path, 'r') as file_:
            return file_.read()

    return ''
