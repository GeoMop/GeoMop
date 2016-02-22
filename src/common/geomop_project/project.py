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
        self.workspace = None
        self.name = None
        self.params = ParameterCollection()
        self.files = FileCollection()
        self.set_project_dir()

    def set_project_dir(self):
        """Sets the correct project dir for files."""
        self.files.project_dir = self.project_dir

    @property
    def project_dir(self):
        if self.filename is None:
            return None
        assert self.filename.endswith(PROJECT_MAIN_FILE), "Invalid project file!"
        return self.filename[:-len(PROJECT_MAIN_FILE)]

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
    def open(workspace, project_name):
        """Retrieve project from settings by its name and workspace."""
        project_filename = os.path.join(workspace, project_name, PROJECT_MAIN_FILE)
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
                project.workspace = workspace
                project.name = project_name
                project.set_project_dir()
                return project

    def save(self):
        """Save the current project into its settings file."""
        assert self.filename is not None, "Project file is not set"
        with open(self.filename, 'w') as project_file:
            yaml.dump(self.dump(), project_file)

    @staticmethod
    def exists(workspace, project_name):
        """Determine whether project exists in a workspace."""
        if not workspace or not project_name:
            return False
        project_filename = os.path.join(workspace, project_name, PROJECT_MAIN_FILE)
        if not os.path.isfile(project_filename):
            return False
        return True

    @staticmethod
    def notify(data):
        """Observer method to update current project."""
        if data.workspace is None or data.project is None:
            Project.current = None
            return
        if (Project.current is None or data.workspace != Project.current.workspace or
                data.project != Project.current.name):
            if Project.exists(data.workspace, data.project):
                project = Project.open(data.workspace, data.project)
                Project.current = project
            else:
                data.project = None
                Project.current = None

    @staticmethod
    def reload_current():
        """Read the current project file and updated the project data."""
        if Project.current is None:
            return None
        project = Project.open(Project.current.workspace, Project.current.name)
        Project.current = project
        return project

    def load_analysis(self, name):
        """Loads a project analysis by its name."""
        from .analysis import ANALYSIS_FILE_EXT, load_analysis_file
        file_path = os.path.join(self.project_dir, name + ANALYSIS_FILE_EXT)
        try:
            return load_analysis_file(file_path)
        except Exception:
            return None

    def save_analysis(self, analysis):
        """Save the analysis within the current project."""
        from .analysis import ANALYSIS_FILE_EXT, save_analysis_file
        file_path = os.path.join(self.project_dir, analysis.name + ANALYSIS_FILE_EXT)
        save_analysis_file(file_path, analysis)
