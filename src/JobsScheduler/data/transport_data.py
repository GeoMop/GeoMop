"""classes for transport"""
from enum import Enum
import json
import abc
import struct
import zlib
import binascii

class ActionType(Enum):
    """Action type"""
    error = 0
    ok = 1
    stop = 2
    installation = 3

class Message:
    """Communication message"""
    def __init__(self, asci = None):
        self.action_type = None
        """type of action"""
        self.json = None
        """json data for action"""
        self.len = None
        """length of data"""
        self.sum = None
        """control sum"""
        if asci is not None:
            self.unpack(asci)
    
    def pack(self):
        """pack data for transport"""
        bin = bytes(self.json, "utf-8")
        bin = struct.pack('!i' , self.action_type.value) + bin
        sum=zlib.crc32(bin)
        bin = struct.pack('!i' , sum) + bin
        length = len(bin)
        bin = struct.pack('!i' , length) + bin
        return binascii.b2a_base64(bin)
        
    def unpack(self, asci):
        """pack data for transport"""
        bin = binascii.a2b_base64(asci)
        self.len, self.sum, action_type = struct.unpack_from("!iii", bin)
        self.action_type = ActionType(action_type)
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
        elif type == ActionType.ok:
            self.data = EmptyData()
        elif type == ActionType.installation:
            self.data = EmptyData()
        elif type == ActionType.error:
            self.data = ErrorData(json_data)
            self.action = ErrorAction(self.data)
        
    def run(self):
        """standart action implementation"""
        self.action.run(self.data)
        
    def get_message(self):
        """return message from action"""
        msg = Message()
        msg.action_type = self.type
        msg.json = self.data.pack()
        return msg

class ErrorAction():
    """Action data"""
    
    def __init__(self, data):
        pass
        
    def run(self, data):
        # ToDo: log
        pass

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

class ErrorData(ActionData):
    """Error data"""
    
    def __init__(self, json_data):
        if json is None:            
            self.data["msg"] = None
        else:
            self.data = json.loads(json_data)
