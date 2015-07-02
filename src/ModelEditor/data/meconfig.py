"""Model dialog static parameters"""
import os
import copy
import config as cfg
import geomop_dialogs
from data.yaml import Loader

__format_dir__ = os.path.join(
    os.path.split(os.path.dirname(os.path.realpath(__file__)))[0], "format")

class _Config:
    """Class for ModelEditor serialization"""

    DEBUG_MODE = False
    """debug mode changes the behaviour"""

    SERIAL_FILE = "ModelEditorData"
    """Serialize class file"""

    COUNT_RECENT_FILES = 5
    """Count of recent files"""

    def __init__(self, readfromconfig=True):
        if readfromconfig:
            data = cfg.get_config_file(self.__class__.SERIAL_FILE)
        else:
            data = None

        if data is not None:
            self.recent_files = copy.deepcopy(data.recent_files)
            self.format_files = copy.deepcopy(data.format_files)
            self.last_data_dir = data.last_data_dir
        else:
            from os.path import expanduser
            self.last_data_dir = expanduser("~")
            self.recent_files = []
            self.format_files = []

    def update_last_data_dir(self, file_name):
        """Save dir from last used file"""
        self.last_data_dir = os.path.dirname(os.path.realpath(file_name))

    def save(self):
        """Save AddPictureWidget data"""
        cfg.save_config_file(self.__class__.SERIAL_FILE, self)

    def add_recent_file(self, file_name, format_file):
        """
        If file is in array, move it top, else add file to top and delete last
        file if is needed. Relevant format files is keep
        """
        #0 files
        if len(self.recent_files) == 0:
            self.recent_files.append(file_name)
            self.format_files.append(format_file)
            self.save()
            return
        #first file == update file
        if file_name == self.recent_files[0]:
            #format file can be changed
            self.format_files[0] = format_file
            self.save()
            return
        #init for
        last_file = self.recent_files[0]
        last_format = self.format_files[0]
        self.recent_files[0] = file_name
        self.format_files[0] = format_file

        for i in range(1, len(self.recent_files)):
            if file_name == self.recent_files[i]:
                #added file is in list
                self.recent_files[i] = last_file
                self.format_files[i] = last_format
                self.save()
                return
            last_file_pom = self.recent_files[i]
            last_format_pom = self.format_files[i]
            self.recent_files[i] = last_file
            self.format_files[i] = last_format
            last_file = last_file_pom
            last_format = last_format_pom
            # recent files is max+1, but first is not displayed
            if self.__class__.COUNT_RECENT_FILES < i+1:
                self.save()
                return
        #add last file
        self.recent_files.append(last_file)
        self.format_files.append(last_format)
        self.save()

    def get_format_file(self, file_name):
        """get format file that is in same position as file"""
        for i in range(0, len(self.recent_files)):
            if self.recent_files[i] == file_name:
                return self.format_files[i]
        return None

class MEConfig:
    """Static data class"""
    format_files = []
    """Array of format files"""
    curr_format_file = None
    """selected format file"""
    config = _Config()
    """Serialized variables"""
    curr_file = None
    """Serialized variables"""
    root = None
    """root DataNode structure"""
    document = ''
    """text set by editor after significant changing"""
    main_window = None
    """parent of dialogs"""
    errors = []
    """array of validation errors"""
    changed = False
    """is file changed"""
    loader = Loader()
    """loader for YAML documents"""

    def __init__(self):
        pass

    @classmethod
    def init(cls, main_window):
        """Init class wit static method"""
        cls._read_format_files()
        cls.main_window = main_window
        if len(cls.config.format_files) > 0:
            cls.curr_format_file = cls.config.format_files[0]
        else:
            if len(cls.format_files) > 0:
                cls.curr_format_file = cls.format_files[0]

    @classmethod
    def _read_format_files(cls):
        """read names of format files in format files directory"""
        from os import listdir
        from os.path import isfile, join
        for file_name in listdir(__format_dir__):
            if (isfile(join(__format_dir__, file_name)) and
                    file_name[-5:].lower() == ".json"):
                cls.format_files.append(file_name[:-5])

    @classmethod
    def get_data_node(cls, line):
        """
        Return dataNode for line number (or preceding DataNode,
        if line number don't show to data node)
        """
        #ToDo:TK

    @classmethod
    def set_current_format_file(cls, file_name):
        """
        set current format file
        """
        if file_name not in cls.format_files:
            return
        cls.curr_format_file = file_name
        cls.update_format()

    @classmethod
    def new_file(cls):
        """
       empty file
        """
        cls.document = ""
        cls.update_format()
        cls.changed = False
        cls.curr_file = None

    @classmethod
    def open_file(cls, file_name):
        """
        read file

        return: if file have good format (boolean)
        """
        try:
            file_d = open(file_name, 'r')
            cls.document = file_d.read()
            file_d.close()
            cls.config.update_last_data_dir(file_name)
            cls.curr_file = file_name
            cls.config.add_recent_file(file_name, cls.curr_format_file)
            cls.update_format()
            cls.changed = False
            return True
        except Exception as err:
            err_dialog = geomop_dialogs.GMErrorDialog(cls.main_window)
            err_dialog.open_error_dialog("Can't open file", err)
        return False

    @classmethod
    def open_recent_file(cls, file_name):
        """
        read file from recent files

        return: if file have good format (boolean)
        """
        format_file = cls.config.get_format_file(file_name)
        if format_file is not None:
            cls.curr_format_file = format_file
        try:
            file_d = open(file_name, 'r')
            cls.document = file_d.read()
            file_d.close()
            cls.config.update_last_data_dir(file_name)
            cls.curr_file = file_name
            cls.config. add_recent_file(file_name, cls.curr_format_file)
            cls.update_format()
            cls.changed = False
            return True
        except Exception as err:
            err_dialog = geomop_dialogs.GMErrorDialog(cls.main_window)
            err_dialog.open_error_dialog("Can't open file", err)
        return False

    @classmethod
    def update(cls):
        """reread yaml text and update node tree"""
        cls.root = cls.loader.load(cls.document)

    @classmethod
    def update_format(cls):
        """reread json format file and update node tree"""
        #ToDo:TK
        cls.update()

    @classmethod
    def save_file(cls):
        """save file"""
        try:
            file_d = open(cls.curr_file, 'w')
            file_d.write(cls.document)
            file_d.close()
            #format is save to recent files up to save file
            cls.config.format_files[0] = cls.curr_format_file
            cls.changed = False
        except Exception as err:
            err_dialog = geomop_dialogs.GMErrorDialog(cls.main_window)
            err_dialog.open_error_dialog("Can't save file", err)

    @classmethod
    def save_as(cls, file_name):
        """save file as"""
        try:
            file_d = open(file_name, 'w')
            file_d.write(cls.document)
            file_d.close()
            cls.config.update_last_data_dir(file_name)
            cls.curr_file = file_name
            cls.config.add_recent_file(file_name, cls.curr_format_file)
            cls.changed = False
        except Exception as err:
            err_dialog = geomop_dialogs.GMErrorDialog(cls.main_window)
            err_dialog.open_error_dialog("Can't save file", err)

    @classmethod
    def update_yaml_file(cls, new_yaml_text):
        """update new editor text"""
        if new_yaml_text != cls.document:
            cls.document = new_yaml_text
            cls.changed = True
            return True
        return False
