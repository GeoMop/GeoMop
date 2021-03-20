import os
from copy import deepcopy

from gm_base.geomop_util import Serializable
import gm_base.config as base_cfg
from LayerEditor.helpers import keyboard_shortcuts_definition as shortcuts_definition
from gm_base.geomop_analysis import Analysis, InvalidAnalysis
from gm_base.geomop_shortcuts import shortcuts

# TODO: refactor config and use JsonData
class _Config:
    """Class for all persistent data which will be saved to config file"""

    __serializable__ = Serializable(
        excluded=['observers']
    )
    SERIAL_FILE = "LayerEditorData"
    """Serialize class file"""

    COUNT_RECENT_FILES = 5
    """Count of recent files"""

    CONFIG_DIR = os.path.join(base_cfg.__config_dir__, 'LayerEditor')

    def __init__(self, **kwargs):
        self._workspace = kwargs.get('_workspace', None)
        self.current_workdir = kwargs.get('current_workdir', os.getcwd())
        """directory of the most recently opened data file"""
        self.recent_files = kwargs.get('recent_files', [])
        """a list of recently opened files"""

    def save(self):
        """Save config data"""
        base_cfg.save_config_file(self.__class__.SERIAL_FILE, self, self.CONFIG_DIR)

    @staticmethod
    def open():
        """Open config from saved file (if exists)."""
        config = base_cfg.get_config_file(_Config.SERIAL_FILE,
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
        """Save last used directory"""
        self.current_workdir = os.path.dirname(os.path.realpath(file_name))

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

    def get_shortcut(self, name):
        """Locate a keyboard shortcut by its action name.

        :param str name: name of the shortcut
        :return: the assigned shortcut
        :rtype: :py:class:`helpers.keyboard_shortcuts.KeyboardShortcut` or ``None``
        """
        shortcut = None
        if name in shortcuts_definition.SYSTEM_SHORTCUTS:
            shortcut = shortcuts_definition.SYSTEM_SHORTCUTS[name]
        elif name in shortcuts_definition.DEFAULT_USER_SHORTCUTS:
            shortcut = shortcuts_definition.DEFAULT_USER_SHORTCUTS[name]
        if shortcut:
            return shortcuts.get_shortcut(shortcut)
        return None
