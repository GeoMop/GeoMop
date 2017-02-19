"""classes for transport"""
from enum import Enum
import json
import abc
import struct
import zlib
import binascii
import logging
from data.states import MJState, TaskStatus

logger = logging.getLogger("Remote")

class ActionType(Enum):
    """Action type"""
    error = 0
    ok = 1
    stop = 2
    installation = 3
    action_in_process = 4
    download_res = 5
    restore_connection = 6
    interupt_connection = 7
    get_state = 8
    state = 9
    add_job = 10
    socket_conn = 11
    job_state = 12
    install_in_process = 13
    set_start_jobs_count = 14
    destroy = 15
    delete = 16
    restore = 17
    ping = 18
    ping_response = 19
    redirect_socket_conn = 20
    socket_reconn_input = 21

class ProcessType(Enum):
    """Action type"""
    ready = 0
    processed = 1
    finished = 2

class Message:
    """
    Communication message
    
    Message is composed of:

        - action type
        - data (:class:`data.transport_data.Action` descendant object in json format)
        - control summation

    Class provides methods for pack and unpack type and data.pack,
    check its len and summation. Data is packed by base64 to ascii
    text format.    
    """
    
    end5 =  "-xXx-"
    """control end of message"""
    
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
        # logger.debug("json:"+self.json)
        bin = bytes(self.json, "utf-8")
        bin = struct.pack('!I' , self.action_type.value) + bin
        sum=zlib.crc32(bin)
        bin = struct.pack('!I' , sum) + bin
        length = len(bin)
        bin = struct.pack('!I' , length) + bin
        #logger.debug("base64:"+str(binascii.b2a_base64(bin),"us-ascii" ).strip())
        
        return str(binascii.b2a_base64(bin),"us-ascii" ).strip() + Message.end5

    @classmethod
    def check_mess(cls, asci):
        """check message to valid end token and valid base 64 format"""
        if len(asci) < len(cls.end5) :
            return False
        if asci[-len(cls.end5):] != cls.end5: 
            return False
        asci = asci[:-len(cls.end5)] 
        try:
            binascii.a2b_base64(asci)
        except:
            return False
        return True
    
    @classmethod
    def is_end_in(cls, txt):
        """in text is message end"""
        text = txt.strip()
        if len(text)<len(cls.end5):
            return False
        if text[-len(cls.end5):] != cls.end5:
            return True
        if cls.end5 in text:
            return True
        return False
    
    def unpack(self, asci):
        """upack transported data from base 64 format"""
        if len(asci) < len(Message.end5) :
            raise MessageError("Invalid message length")
        if asci[-len(Message.end5):] != Message.end5: 
            raise MessageError("Invalid end of token")
        asci = asci[:-len(Message.end5)] 
        try:
            bin = binascii.a2b_base64(asci)
        except:
            raise MessageError("Invalid base64 data format")
        try:
            self.len, self.sum, action_type = struct.unpack_from("!III", bin)
        except(struct.error) as err:
            raise MessageError("Unpact error: " + str(err))
        if self.len != (len(bin)-struct.calcsize("!I")):
            raise MessageError("Invalid data length")
        try:
            self.action_type = ActionType(action_type)
        except:
            raise MessageError("Invalid action type")
        sum = zlib.crc32(bin[struct.calcsize("!II"):])
        if sum != self.sum:
            raise MessageError("Invalid checksum")
        self.json = bin[struct.calcsize("!III"):].decode("utf-8")
        
    def get_action(self):
        action = Action(self.action_type, self.json)
        return action
        
class MessageError(Exception):
    """Error in message format"""
    
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
        if type == ActionType.stop:
            self.data = EmptyData()
        elif type == ActionType.ok:
            self.data = EmptyData()
        elif type == ActionType.restore:
            self.data = EmptyData()
        elif type == ActionType.restore_connection:
            self.data = EmptyData()
        elif type == ActionType.interupt_connection:
            self.data = EmptyData()
        elif type == ActionType.installation:
            self.data = EmptyData()
        elif type == ActionType.download_res:
            self.data = EmptyData()
        elif type == ActionType.delete:
            self.data = EmptyData()
        elif type == ActionType.action_in_process:
            self.data = EmptyData()
        elif type == ActionType.error:
            self.data = ErrorData(json_data)
        elif type == ActionType.get_state:
            self.data = EmptyData()
        elif type == ActionType.state:
            self.data = StateData(json_data)
        elif type == ActionType.job_state:
            self.data = JobStateData(json_data)            
        elif type == ActionType.add_job:
            self.data = JobData(json_data)
        elif type == ActionType.socket_conn:
            self.data = SocketConn(json_data)
        elif type == ActionType.install_in_process:
            self.data = InstallData(json_data)
        elif type == ActionType.set_start_jobs_count:
            self.data = StartCountsData(json_data)
        elif type == ActionType.destroy:
            self.data = ErrorData(json_data)
        elif type == ActionType.ping:
            self.data = EmptyData()
        elif type == ActionType.ping_response:
            self.data = EmptyData()
        elif type == ActionType.redirect_socket_conn:
            self.data = EmptyData()
        elif type == ActionType.socket_reconn_input:
            self.data = EmptyData()
            
    def get_message(self):
        """return message from action"""
        msg = Message()
        msg.action_type = self.type
        msg.json = self.data.pack()
        return msg

class ActionData(metaclass=abc.ABCMeta):
    """Action data"""
    
    def __init__(self, json_data=None):
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
    
    def __init__(self, json_data=None):
        self.data={}
        if json_data is None:            
            self.data["msg"] = None
            self.data["severity"] = 0 
        else:
            self.data = json.loads(json_data) 
 
class InstallData(ActionData):
    """Install data"""

    def __init__(self, json_data=None):
        self.data={}
        if json_data is None:            
            self.data["phase"] = TaskStatus.installation.value
        else:
            self.data = json.loads(json_data)

class JobData(ActionData):
    """Data for adding new job over remote"""    
    def __init__(self, json_data=None):
        self.data={}
        if json_data is None:            
            self.data["id"] = None
        else:
            self.data = json.loads(json_data)
    
    def set_id(self, id):
        """Set job id"""
        self.data["id"] = id

class SocketConn(ActionData):
    """Connection parameters of a new job over remote"""
    def __init__(self, json_data=None):
        self.data={}
        if json_data is None:            
            self.data["host"] = None
            self.data["port"] = None
        else:
            self.data = json.loads(json_data)

    def set_conn(self, host, port):
        """Set connection data"""
        self.data["host"] = host
        self.data["port"] = port

class StateData(ActionData):
    """Multijob status data. Data is set by 
    (:class:`data.states.MJState`) """    
    def __init__(self, json_data=None):
        self.data={}
        if json_data is  not None:
            self.data = json.loads(json_data) 

    def set_data(self, mjstate):
        """fill data by MJState class"""
        self.data = mjstate.__dict__
        self.data['status'] = self.data['status'].value

    def get_mjstate(self, mjname):
        """return MJState class instance"""
        state = MJState(mjname)        
        state.__dict__ = self.data
        state.status = TaskStatus(state.status)
        return state

class StartCountsData(ActionData):
    """Inicialize job state structure in remote communicator."""
    def __init__(self, json_data=None):
        self.data={}
        if json_data is  not None:
            self.data = json.loads(json_data) 
        else:
            self.data["estimated_jobs"] = 0
            self.data["known_jobs"] = 0
    
    def set_data(self, known_jobs, estimated_jobs):
        """fill JobState state"""
        self.data["known_jobs"] = known_jobs
        self.data["estimated_jobs"] = estimated_jobs
            
class JobStateData(ActionData):
    """Job status data."""    
    def __init__(self, json_data=None):
        self.data={}
        if json_data is  not None:
            self.data = json.loads(json_data) 
        else:
            self.data["ready"] = False
            self.data["return_code"] = 0
    
    def set_data(self, return_code):
        """fill JobState state"""
        if return_code is None:
            self.data["ready"] = False
            self.data["return_code"] = 0
        else:
            self.data["ready"] = True
            self.data["return_code"] = return_code
