"""class represent instalation"""
import os

__install_dir__ = os.path.split(os.path.split(
    os.path.dirname(os.path.realpath(__file__)))[0])[0]
__ins_files__ = {}
__ins_files__['delegator'] =os.path.join(__install_dir__, "delegator.py")
__ins_dir__ = []
__ins_dir__.append(os.path.join(__install_dir__, "communication"))
__ins_dir__.append(os.path.join(__install_dir__, "data"))
__ins_dir__.append(os.path.join(__install_dir__, "twoparty"))

class Installation:
    """Files with installation (python files and configuration files) is selected 
        and send to set folder"""
    def __init__(self):
        self.copy_path = None
        """installation file path"""
        
    def copy(self,  new_dir):
        """Copy installation files"""
        exist=True
        self.copy_path =  new_path
        
    def run_python_file(self, name):
        """Find install file according to name and return command for running"""
