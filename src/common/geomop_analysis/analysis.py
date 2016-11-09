"""
.. codeauthor:: Tomas Krizek <tomas.krizek1@tul.cz>
"""

import os

from geomop_util import Serializable, Parameter, File
import config
import flow_util


ANALYSIS_MAIN_FILE_EXT = 'data'
ANALYSIS_MAIN_FILE_NAME = 'analysis'
ANALYSIS_MAIN_FILE = ANALYSIS_MAIN_FILE_NAME + '.' + ANALYSIS_MAIN_FILE_EXT
MULTIJOBS_DIR = 'mj'
CONFIG_DIR = '.settings'
MJ_CONFIG_DIR = 'mj_input'


class InvalidAnalysis(Exception):
    pass


class Analysis:
    """Analysis settings and data."""

    __serializable__ = Serializable(
        excluded=['filename',
                  'workspace',
                  'name',
                  'analysis_dir',
                  '_analysis_dir'],
        composite={'params': Parameter,
                   'files': File,
                   'additional_files': File}
    )

    current = None
    """currently opened analysis"""

    def __init__(self, filename=None, **kwargs):
        self.filename = filename
        self.workspace = None
        self.name = None
        self.params = kwargs['params'] if 'params' in kwargs else []
        self.files = kwargs['files'] if 'files' in kwargs else []
        self.additional_files = kwargs['additional_files'] if 'additional_files' in kwargs else []
        self._analysis_dir = ''
        self.flow123d_version = kwargs['flow123d_version'] if 'flow123d_version' in kwargs else ''
        self.mj_counter = kwargs['mj_counter'] if 'mj_counter' in kwargs else 1

    @staticmethod
    def _get_compare_path(path):
        """return uppercase normalized real path"""
        if path is None:
            return None
        res=os.path.realpath(path)
        return os.path.normcase(res)

    @property
    def analysis_dir(self):
        return self._analysis_dir

    @analysis_dir.setter
    def analysis_dir(self, value):
        self._analysis_dir = self. _get_compare_path(value)

    @property
    def selected_file_paths(self):
        return [f.file_path for f in (self.files + self.additional_files) if f.selected]

    @staticmethod
    def open(workspace, analysis_name, sync_files=False):
        """Retrieve analysis from settings by its name and workspace."""
        if analysis_name is None:
            raise InvalidAnalysis("No analysis specified.")
        if workspace is None:
            raise InvalidAnalysis("No workspace specified.")
        directory = os.path.join(workspace, analysis_name)
        analysis = config.get_config_file(ANALYSIS_MAIN_FILE_NAME,
                                          directory=directory,
                                          extension=ANALYSIS_MAIN_FILE_EXT,
                                          cls=Analysis)
        if analysis is None:
            raise InvalidAnalysis("Current analysis is invalid.")

        analysis.analysis_dir = directory
        analysis.filename = os.path.join(directory, ANALYSIS_MAIN_FILE)
        analysis.workspace = workspace
        analysis.name = analysis_name

        # scan and update files
        if sync_files:
            current_configs = {file.file_path: file for file in analysis.files}
            current_additional_files = {file.file_path: file for file in analysis.additional_files}
            analysis.files = []
            analysis.additional_files = []
            for root, dirs, files in os.walk(analysis.analysis_dir):
                # ignore multijobs folder
                if root.startswith(os.path.join(analysis.analysis_dir, MULTIJOBS_DIR)):
                    continue

                for filename in files:
                    file_path = analysis.make_relative_path(os.path.join(root, filename))
                    if file_path.endswith('.yaml'):
                        if file_path in current_configs:
                            analysis.files.append(current_configs[file_path])
                        else:
                            analysis.files.append(File(file_path))
                    else:
                        if filename == ANALYSIS_MAIN_FILE:
                            continue
                        elif file_path in current_additional_files:
                            analysis.additional_files.append(current_additional_files[file_path])
                        else:
                            analysis.additional_files.append(File(file_path))

        return analysis

    @staticmethod
    def open_from_mj(mj_dir, analysis_name='N/A'):
        """Retrieve analysis from multijob directory."""
        analysis = config.get_config_file(ANALYSIS_MAIN_FILE_NAME,
                                          directory=os.path.join(mj_dir , MJ_CONFIG_DIR),
                                          extension=ANALYSIS_MAIN_FILE_EXT,
                                          cls=Analysis)
        if analysis is None:
            raise InvalidAnalysis("Current analysis is invalid.")

        analysis.analysis_dir = mj_dir
        analysis.filename = os.path.join(mj_dir, ANALYSIS_MAIN_FILE)
        analysis.workspace = None
        analysis.name = analysis_name

        return analysis

    @staticmethod
    def exists(workspace, analysis_name):
        """Determine whether project exists in a workspace."""
        if not workspace or not analysis_name:
            return False
        analysis_filename = os.path.join(workspace, analysis_name, ANALYSIS_MAIN_FILE)
        if not os.path.isfile(analysis_filename):
            return False
        return True

    @staticmethod
    def notify(data):
        """Observer method to update current analysis."""
        if data.workspace is None or data.analysis is None:
            Analysis.current = None
            return
        if (Analysis.current is None or data.workspace != Analysis.current.workspace or
                data.analysis != Analysis.current.name):
            if Analysis.exists(data.workspace, data.analysis):
                Analysis.current = Analysis.open(data.workspace, data.analysis)
            else:
                data.analysis = None
                Analysis.current = None

    @staticmethod
    def reload_current():
        """Read the current analysis file and updated the analysis data."""
        if Analysis.current is None:
            return None
        analysis = Analysis.open(Analysis.current.workspace, Analysis.current.name)
        analysis._sync_analysis()
        Analysis.current = analysis
        return analysis

    def save(self):
        """Save the current analysis as a config file."""
        config.save_config_file(ANALYSIS_MAIN_FILE_NAME, self, self._analysis_dir,
                                ANALYSIS_MAIN_FILE_EXT)

    def make_relative_path(self, file_path):
        """Makes the path relative to analysis_dir."""
        file_path = self. _get_compare_path(file_path)
        if not self._analysis_dir:
            return file_path
        if not file_path.startswith(self._analysis_dir):
            # assume file_path is already relative to project
            return file_path
        return file_path[len(self._analysis_dir)+1:]

    def merge_params(self, params):
        """Merge another param collection into this one."""
        for new_param in params:
            # check if param doesn't exist, then add it
            exists = False
            for curr_param in self.params:
                if curr_param.name == new_param.name:
                    exists = True
                    break
            if not exists:
                self.params.append(new_param)

    def is_abs_path_in_analysis_dir(self, file_path):
        """Whether file exists in the analysis directory or subdirectories."""
        file_path = self. _get_compare_path(file_path)
        if not file_path or not self._analysis_dir:
            return False
        return file_path.startswith(self._analysis_dir)

    def add_file(self, file_path, params=None):
        """Add or sync a file. If file exists, update parameters."""
        file_path = self.make_relative_path(file_path)
        for file in self.files:
            if file_path == file.file_path:
                if params is not None:
                    file.params = params
                return
        # file is not registered
        file = File(file_path, params)
        self.files.append(file)
        return

    def _sync_analysis(self):
        """Write current file and params to an analysis file."""
        if len(self._analysis_dir)==0 or not os.path.isdir(self._analysis_dir):
            return
        for root, directories, filenames in os.walk(self._analysis_dir):
            for filename in filenames:
                if filename.endswith('.yaml') and \
                        not "analysis_results" in root:
                    self.add_file(os.path.join(root, filename))
        self.save()

    def copy_into_mj_folder(self, mj):
        """Copy this analysis into multijob folder."""
        mj_dir = os.path.join(self.analysis_dir, MULTIJOBS_DIR, mj.preset.name, MJ_CONFIG_DIR)
        if not os.path.isdir(mj_dir):
            os.makedirs(mj_dir)

        # get all files used by analyses
        files = self.selected_file_paths
        # add analysis configuration file
        files.append(ANALYSIS_MAIN_FILE)

        # get parameters
        params = {param.name: param.value for param in self.params if param.value}

        # copy the selected files (with filled in parameters)
        for file in set(files):
            src = os.path.join(self.analysis_dir, file)
            dst = os.path.join(mj_dir, file)
            # create directory structure if not present
            dst_dir = os.path.dirname(dst)
            if not os.path.isdir(dst_dir):
                os.makedirs(dst_dir)
            flow_util.analysis.replace_params_in_file(src, dst, params)

    @staticmethod
    def is_analysis(path):
        """Determine if a path is an analysis directory."""
        if os.path.isdir(path):
            if path.endswith(CONFIG_DIR):
                return False
            for file_ in os.listdir(path):                
                if file_.lower() == ANALYSIS_MAIN_FILE:
                    return True
        return False

    @staticmethod
    def list_analyses_in_workspace(workspace):
        """Get a list of all analyses in workspace."""
        analyses = []
        if os.path.exists(workspace):
            for name in os.listdir(workspace):
                path = os.path.join(workspace, name)
                if Analysis.is_analysis(path):
                    analyses.append(name)
        return analyses
        
    @staticmethod
    def get_workspace_config_dir(workspace, module):
        """Get a list of all analyses in workspace."""
        if os.path.exists(workspace):
            settings = os.path.join(workspace,CONFIG_DIR)
            if not os.path.exists(settings):
                os.makedirs(settings)
            settings = os.path.join(settings, module)
            if not os.path.exists(settings):
                os.makedirs(settings)
            return settings
        return None
