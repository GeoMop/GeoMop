import os
from copy import deepcopy

from gm_base.geomop_util import Serializable
import gm_base.config as cfg
from LayerEditor.helpers import keyboard_shortcuts_definition as shortcuts_definition
from gm_base.geomop_analysis import Analysis, InvalidAnalysis


class _Config:
    """Class for Analyzis serialization"""

    __serializable__ = Serializable(
        excluded=['observers']
    )
    #
    # DEBUG_MODE = False
    # """debug mode changes the behaviour"""
    #
    SERIAL_FILE = "LayerEditorData"
    """Serialize class file"""

    COUNT_RECENT_FILES = 5
    """Count of recent files"""

    # CONTEXT_NAME = 'LayerEditor'
    #
    CONFIG_DIR = os.path.join(cfg.__config_dir__, 'LayerEditor')

    def __init__(self, **kwargs):

        # self.observers = []
        # """objects to be notified of changes"""
        # self._analysis = None
        # self._workspace = None
        #
        # self._analysis = kwargs.get('_analysis', None)
        self._workspace = kwargs.get('_workspace', None)
        self.show_init_area = kwargs.get('show_init_area', True)


        # self.show_init_area = kwargs.get('show_init_area', True)
        #
        self.current_workdir = os.getcwd()
        """directory of the most recently opened data file"""
        self.recent_files = kwargs.get('recent_files', [])
        """a list of recently opened files"""
        #
        # self.shortcuts = kwargs.get('shortcuts',
        #                            deepcopy(shortcuts_definition.DEFAULT_USER_SHORTCUTS))
        # """user customizable keyboard shortcuts"""

    def save(self):
        """Save config data"""
        cfg.save_config_file(self.__class__.SERIAL_FILE, self, self.CONFIG_DIR)

    @staticmethod
    def open():
        """Open config from saved file (if exists)."""
        config = cfg.get_config_file(_Config.SERIAL_FILE,
                                     _Config.CONFIG_DIR, cls=_Config)
        if config is None:
            config = _Config()
        return config

    def add_recent_file(self, file_name):
        """
        If file is in array, move it top, else add file to top and delete last
        file if is needed. Relevant format files is keep
        """
        # 0 files
        if len(self.recent_files) == 0:
            self.recent_files.append(file_name)
            self.save()
            return
        # init for
        if self.recent_files[0] == file_name:
            self.save()
            return
        last_file = self.recent_files[0]
        self.recent_files[0] = file_name

        for i in range(1, len(self.recent_files)):
            if file_name == self.recent_files[i]:
                # added file is in list
                self.recent_files[i] = last_file
                self.save()
                return
            last_file_pom = self.recent_files[i]
            self.recent_files[i] = last_file
            last_file = last_file_pom
            # recent files is max+1, but first is not displayed
            if self.__class__.COUNT_RECENT_FILES < i+1:
                self.save()
                return
        # add last file
        self.recent_files.append(last_file)
        self.save()

    @property
    def data_dir(self):
        """Data directory - either an analysis dir or the last used dir."""
        if self.workspace and self.analysis:
            return os.path.join(self.workspace, self.analysis)
        else:
            return self.current_workdir

    def update_current_workdir(self, file_name):
        """Save dir from last used file"""
        analysis_directory = None
        directory = os.path.dirname(os.path.realpath(file_name))
        if self.workspace is not None and self.analysis is not None:
            analysis_dir = os.path.join(self.workspace, self.analysis)
        if analysis_directory is None or directory != analysis_dir:
            self.current_workdir = directory

    @property
    def workspace(self):
        """path to workspace"""
        return self._workspace

    @workspace.setter
    def workspace(self, value):
        if value == '' or value is None:
            self._workspace = None
        if value != self._workspace:
            # close analysis if workspace is changed
            self.analysis = None
        self._workspace = value

    # @property
    # def analysis(self):
    #     """name of the analysis in the workspace"""
    #     return self._analysis

    # @analysis.setter
    # def analysis(self, value):
    #     if value == '' or value is None:
    #         self._analysis = None
    #         Analysis.current = None
    #     else:
    #         self._analysis = value
    #         try:
    #             analysis = Analysis.open(self._workspace, self._analysis)
    #         except InvalidAnalysis:
    #             self._analysis = None
    #         else:
    #             Analysis.current = analysis
    #     self.notify_all()

    # def notify_all(self):
    #     """Notify all observers about changes."""
    #     for observer in self.observers:
    #         observer.config_changed()


