"""Configuration of communication unit"""
from enum import Enum
import logging

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
        self.communicator_name = ""
        """this communicator name for login file, ..."""
        self.next_communicator = ""
        """communicator file that will be start"""
        self.host = "127.0.0.1"
        """Host (ip or dns) for output configuration"""
        self.uid = ""
        """User for output configuration"""
        self.pwd = ""
        """Password for output configuration"""
        self.log_level = logging.WARNING
        """log level for communicator"""
