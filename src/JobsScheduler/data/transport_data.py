"""classes for transport"""
from enum import Enum
import json
import abc
import struct
import zlib
import binascii
import logging

class ActionType(Enum):
    """Action type"""
    error = 0
    ok = 1
    stop = 2
    installation = 3
    action_in_process = 4

class Message:
    """
    Communication message
    
    Message is compose from:
      - action type
      - data (:class:`data.transport_data.Action` descendant object in json format)
      - controll summation
    Class provide method for pack and unpack type and data.pack,
    check its len and summation. Data is pack by base64 to ascii
    text format.    
    """
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
    
    def __str__(self):
        """string representation"""
        if isinstance(self.action_type, ActionType):
            t = str(self.action_type)[ len(type(self.action_type).__name__)+1:]
        else:
            if self.action_type is None:
                t = "None"
            else:
                t = "unknown type"
        if self.json is None:
            a = "None"
        else:
            a = self.json
        return "type:{}, action{}".format(t, a)
    
    def pack(self):
        """pack data for transport to base64 format"""
        import logging
        logging.debug("json:"+self.json)
        bin = bytes(self.json, "utf-8")
        bin = struct.pack('!i' , self.action_type.value) + bin
        sum=zlib.crc32(bin)
        bin = struct.pack('!i' , sum) + bin
        length = len(bin)
        bin = struct.pack('!i' , length) + bin
        return str(binascii.b2a_base64(bin),"us-ascii" ).strip()
        
    def unpack(self, asci):
        """upack transported data from base 64 format"""
        try:
            bin = binascii.a2b_base64(asci)
        except:
            raise MessageError("Invalid base64 data format")
        try:
            self.len, self.sum, action_type = struct.unpack_from("!iii", bin)
        except(struct.error) as err:
            raise MessageError("Unpact error: " + str(err))
        if self.len != (len(bin)-struct.calcsize("!i")):
            raise MessageError("Invalid data length")
        try:
            self.action_type = ActionType(action_type)
        except:
            raise MessageError("Invalid action type")
        sum = zlib.crc32(bin[struct.calcsize("!ii"):])
        if sum != self.sum:
            raise MessageError("Invalid checksum")
        self.json = bin[struct.calcsize("!iii"):].decode("utf-8")
        
class MessageError(Exception):
    """Error in nessage format"""
    
    def __init__(self, msg):
        super(MessageError, self).__init__(msg)

class Action():
    """
    Action entry class
    
    Action descendant represent data types, that is saved as data in
    :class:`data.transport_data.Message` class. This descendant classes
    provide implementation of pack funcion, that serve Action for
    serialization data to message
    """
    
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
        elif type == ActionType.action_in_process:
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
        logging.error("Error message is received: " + data["msg"])
        pass

class ActionData(metaclass=abc.ABCMeta):
    """Action data"""
    
    def __init__(self, json_data):
        self.data={}
        """Data for json packing"""
    
    def pack(self):
        """Data packing to json"""
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
        self.data={}
        if json_data is None:            
            self.data["msg"] = None
        else:
            self.data = json.loads(json_data)
