"""class represent instalation"""
import os

__install_dir__ = os.path.split(os.path.split(
    os.path.dirname(os.path.realpath(__file__)))[0])[0]
__ins_files__ = {}
__ins_dir__ = []
__ins_dir__.append(os.path.join(__install_dir__, "communication"))
__ins_dir__.append(os.path.join(__install_dir__, "data"))

class Installation:
    """Files with installation is palased in zip and is unpack to set folder"""
    def __init__(self):
        self.copy_path = None
        """installation file path"""
        
    def copy(self,  new_path):
        """Copy installation files"""
        self.copy_path =  new_path
