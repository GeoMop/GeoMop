"""
Module contains version.

.. codeauthor:: Tomas Krizek <tomas.krizek1@tul.cz>
"""

import os
from ruamel.yaml import YAML

__root_path__ = (os.path.split(os.path.dirname(os.path.realpath(__file__)))[0])


def get_root_file_path(filename):
    """File path to a file in a root folder."

    Git repo has has a different place for root than installed version of app.
    """
    file_path = os.path.join(__root_path__, filename)  # installed on Win
    if not os.path.isfile(file_path):
        file_path = os.path.join(__root_path__, '..', filename)  # for git repo
    return file_path


class Version:
    """Geomop version module"""

    def __init__(self):
        """Initializes the class."""
        try:
            yaml = YAML(typ='safe')  # default, if not specfied, is 'rt' (round-trip)
            content = yaml.load(Version.VERSION_FILE_PATH)
        except FileNotFoundError:
            lines = []

        self.version = content['version']
        """text version geomop pressentation"""
        self.build = content['build']
        """text build geomop pressentation"""
        self.date = content['date']
        """text date geomop pressentation"""

    CHANGELOG_FILE_PATH = get_root_file_path('CHANGELOG.md')
    VERSION_FILE_PATH = get_root_file_path('version.yml')

