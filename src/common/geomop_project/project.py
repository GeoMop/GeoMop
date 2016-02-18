"""
.. codeauthor:: Tomas Krizek <tomas.krizek1@tul.cz>
"""

import os
import yaml

from .collections import YAMLSerializable, ParameterCollection, FileCollection


PROJECT_MAIN_FILE = 'main.yaml'


class InvalidProject(Exception):
    pass


class Project(YAMLSerializable):
    """Project settings and data."""

    current = None
    """currently opened project"""

    def __init__(self, filename=None):
        self.filename = filename
        self.params = ParameterCollection()
        self.files = FileCollection()
        self.set_project_dir()

    def set_project_dir(self):
        """Sets the correct project dir for files."""
        if self.filename is None:
            return
        assert self.filename.endswith(PROJECT_MAIN_FILE), "Invalid project file!"
        self.files.project_dir = self.filename[:-len(PROJECT_MAIN_FILE)]

    @staticmethod
    def load(data):
        project = Project()
        if data is None:
            return project
        if 'params' in data:
            project.params = ParameterCollection.load(data['params'])
        if 'files' in data:
            project.files = FileCollection.load(data['files'])
        return project

    def dump(self):
        return dict(params=self.params.dump(),
                    files=self.files.dump())

    @staticmethod
    def open(workspace, project):
        """Retrieve project from settings by its name and workspace."""
        project_filename = os.path.join(workspace, project, PROJECT_MAIN_FILE)
        if not os.path.isfile(project_filename):
            raise InvalidProject("Current project is invalid.")
        else:
            try:
                with open(project_filename) as project_file:
                    data = yaml.load(project_file)
                project = Project.load(data)
            except Exception:
                raise InvalidProject("Could not load project settings.")
            else:
                project.filename = project_filename
                project.set_project_dir()
                return project

    def save(self):
        """Save the current project into its settings file."""
        assert self.filename is not None, "Project file is not set"
        with open(self.filename, 'w') as project_file:
            yaml.dump(self.dump(), project_file)
