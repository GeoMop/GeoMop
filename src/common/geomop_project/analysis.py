"""Analysis - class + load/save functions.

.. codeauthor:: Tomas Krizek <tomas.krizek1@tul.cz>
"""

import json

from .collections import YAMLSerializable


ANALYSIS_FILE_EXT = '.anal'


class Analysis(YAMLSerializable):
    def __init__(self, name, files=None, params=None):
        self.name = name
        """name of the analysis"""
        self.files = []
        """a list of files used in analysis"""
        self.params = {}
        """key: value pairs of parameter values"""
        if files is not None and isinstance(files, list):
            self.files = files
        if params is not None and isinstance(params, dict):
            self.params = params

    @property
    def filename(self):
        """filename of the analysis"""
        return self.name + ANALYSIS_FILE_EXT

    @staticmethod
    def load(data):
        kwargs = {}
        if 'name' in data:
            kwargs['name'] = data['name']
        if 'files' in data:
            kwargs['files'] = data['files']
        if 'params' in data:
            kwargs['params'] = data['params']
        return Analysis(**kwargs)

    def dump(self):
        return dict(name=self.name,
                    files=self.files,
                    params=self.params)


def load_analysis_file(file_path):
    """Load the analysis files."""
    with open(file_path) as file:
        data = json.load(file)
        analysis = Analysis.load(data)
    return analysis


def save_analysis_file(file_path, analysis):
    """Load the analysis files."""
    with open(file_path, 'w') as file:
        json.dump(analysis.dump(), file)
