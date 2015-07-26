"""classes for transport"""
from enum import Enum
from data.Instalation import Instalation
import json
import abc
import struct
import zlib

class ActionType(Enum):
    """Action type"""
    stop = 0
    installation = 1

class Message:
    """Communication message"""
    def __init__(self, bin = None):
        self.action_type
        """type of action"""
        self.json
        """json data for action"""
        self.len
        """length of data"""
        self.sum
        """control sum"""
        if bin is not None:
            self.unpack(bin)
    
    def pack(self):
        """pack data for transport"""
        bin = bytes(self.json, "utf-8")
        bin = struct.pack('!i' , self.action_type) + bin
        sum=zlib.crc32(bin)
        bin = struct.pack('!i' , sum) + bin
        length = len(bin)
        bin = struct.pack('!i' , length) + bin        
        
    def unpack(self, bin):
        """pack data for transport"""
        self.len, self.sum, self.action_type = struct.unpack_from("!iii", bin)
        sum = zlib.crc32(bin[struct.calcsize("!ii"):])
        if sum != self.sum:
            raise Exception("Invalid checksum")
        self.json = bin[struct.calcsize("!iii"):].decode("utf-8")

class Action():
    """Action entry class"""
    
    def __init__(self,  type, json_data=None):
        self.type = type
        """action type"""
        self.data = None
        """data for action"""
        self.action = None
        """typed action"""
        if type == ActionType.stop:
            self.data = EmptyData()
        if type == ActionType.installation:
            self.data = InstallationData(json_data)
            self.action = InstallationAction(self.data)
        
    def run(self):
        self.action.run(self.data)
        
    def pack(self):
        self.data.parse()

class InstallationAction():
    """Action data"""
    
    def __init__(self, data):
        pass
        
    def run(self, data):
        installatin = Instalation()
        installatin.copy(data.path)

class ActionData(metaclass=abc.ABCMeta):
    """Action data"""
    
    def __init__(self, json_data):
        self.data={}
        """Data for json packing"""
    
    def pack(self):
        """Data packing"""
        return json.dumps(self.data)

class EmptyData(ActionData):
    """Empty data"""
    
    def __init__(self):
        pass

    def pack(self):
        """Data packing"""
        return json.dumps({})

class InstallationData(ActionData):
    """Action data"""
    
    def __init__(self, json_data):
        if json is None:            
            self.data["path"] = None
        else:
            self.data = json.loads(json_data)
