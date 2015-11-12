"""
Module contains helper functions for loading stylesheets.

.. codeauthor:: Tomas Krizek <tomas.krizek1@tul.cz>
"""

import os


def load_stylesheet(path):
    """Loads the stylesheet file to a string.

    :param str path: absolute path to the stylesheet
    :return: stylesheet loaded as text
    :rtype: str
    """
    if os.path.isfile(path):
        with open(path) as file_:
            return file_.read()

    return ''
