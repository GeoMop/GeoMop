"""Model dialog static parameters"""
import os
import copy
import config as cfg
import geomop_dialogs

__format_dir__=os.path.join(os.path.split(os.path.dirname(os.path.realpath(__file__)))[0], "format")

class _Config():
    """Class for ModelEditor serialization"""
    
    SERIAL_FILE = "ModelEditorData"    
    """Serialize class file"""
    
    COUNT_RECENT_FILES = 5    
    """Count of recent files"""
    
    def __init__(self, readfromconfig = True):        
        if readfromconfig:
            data=cfg.get_config_file(self.__class__.SERIAL_FILE)
        else:
            data=None
            
        if(data != None):
            self.recent_files = copy.deepcopy(data.recentFiles)
            self.format_files = copy.deepcopy(data.last_format_files)     
        else:
            self.recent_files = []
            self.format_files = []
      
    def save(self):
        """Save AddPictureWidget data"""
        cfg.save_config_file(self.__class__.SERIAL_FILE, self)
       
    def add_recent_file(self,  file,  format_file):
        """
        If file is in array, move it top, else add file to top and delete last 
        file if is needed. Relevant format files is keep
        """
        #ToDo:

class MEConfig():
    
    format_files = []
    """Array of format files"""
    curr_format_file = None
    """selected format file"""
    config = _Config()
    """Serialized variables"""
    curr_file = None
    """Serialized variables"""
    root=None
    """root DataNode structure"""
    yaml_text=None   
    
    @classmethod
    def init(cls):
        """Init class wit static method"""
        cls._read_format_files()
        if len(cls.config.format_files) > 0:
            cls.curr_format_file = cls.config.last_format_files[0]
        else:
            if len(cls.format_files)>0:
                cls.curr_format_file = cls.format_files[0]

    @classmethod    
    def _read_format_files(cls):
        """read names of format files in format files directory"""
        from os import listdir
        from os.path import isfile, join
        for file in listdir(__format_dir__):
                if isfile(join(__format_dir__,file)) and file[-5:].lower() == ".json":
                    cls.format_files.append(file[:-5])

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
        cls.curr_format_file = file_name
        cls.update_format()

    @classmethod
    def open_file(cls, file_name):
        """
        read file
        
        return: if file have good format (boolean)
        """
        try:
            file = open(file_name, 'r')
            cls.yaml_text = file.read()
            cls.curr_file = file_name;
            cls.config. add_recent_file(file_name, cls.curr_format_file)
            cls.update_format()
            return True
        except Exception as err:
            err_dialog=geomop_dialogs.GMErrorDialog()
            err_dialog.exec("Can't open file", err)
        return False

    @classmethod
    def update(cls):
        """reread yaml text and update node tree"""
        #ToDo:TK
    
    @classmethod
    def update_format(cls):
        """reread json format file and update node tree"""
        #ToDo:TK
        cls.update()

    @classmethod
    def save_file(cls):
        """save file"""
        try:
            file = open(cls.curr_file, 'w')
            file.write(cls.yaml_text)            
        except Exception as err:
            err_dialog=geomop_dialogs.GMErrorDialog()
            err_dialog.exec("Can't save file", err)

