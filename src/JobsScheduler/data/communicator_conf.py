"""Configuration of communication unit"""
from enum import Enum

class OutputCommType(Enum):
    """Severity of an error."""
    none = 0
    ssh = 1
    ssh_screen = 2
    pbs = 3
    
class InputCommType(Enum):
    """Severity of an error."""
    none = 0
    std = 1
    file = 2
    pbs = 3

class CommunicatorConfig():
    """Communicator Configuration"""
    
    def __init__(self):
        self.input_type = InputCommType.none
        """Input communication type"""
        self.output_type = OutputCommType.none
        """Output communication type"""
        self.install_path = False
        """
        copy and instal before running to this path
        
        None - not install
        Absoluth path
        Relative path
        """
        self.next_communicator
        """communicator file that will be start"""
        self.host = "127.0.0.1"
        """Host (ip or dns) for output configuration"""
        self.uid = ""
        """User for output configuration"""
        self.pwd = ""
        """Password for output configuration"""
