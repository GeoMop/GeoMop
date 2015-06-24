import copy
import config as cfg

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
            recent_files = copy.deepcopy(data.recentFiles)
            last_format_file = data.last_format_file     
        else:
            recent_files = []
            last_format_file = None
      
    def save(self):
        """Save AddPictureWidget data"""
        cfg.save_config_file(self.__class__.SERIAL_FILE, self)
       
    def add_recent_file(self,  file):
        """If file is in array, move it top, else add file to top and delete last file if is needed"""

class MEConfig():
    
    format_files = []
    """Array of format files"""
    config = _Config()
    """Serialized variables"""
    curr_file = None
    """Serialized variables"""
    root=None
    """root node"""
    
    @classmethod
    def init(cls):
        """Init class wit static method"""
        cls._readFormatFiles()
        if cls.config.last_format_file == None  and len(format_files)>0:
            cls.config.last_format_file = format_files[0]
    
    @classmethod    
    def _readFormatFiles(cls):
        """read names of format files in format files directory"""

    def readFile(cls, file_name):
        """read file
        
        return: if file have good format (boolean)
        """
        return False
        
    def saveFile(cls):
        """save file"""


