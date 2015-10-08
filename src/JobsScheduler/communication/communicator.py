"""Class for communacion"""
import sys
import logging
import os
import time
import threading
import data.communicator_conf as comconf
import data.transport_data as tdata
from communication.std_input_comm import StdInputComm
from  communication.socket_input_comm import SocketInputComm
from  communication.ssh_output_comm import SshOutputComm
from  communication.exec_output_comm import  ExecOutputComm
from  communication.installation import  Installation
from  communication.pbs_output_comm import PbsOutputComm
from  communication.pbs_input_comm import PbsInputComm

LONG_MESSAGE_TIMEOUT=600

class Communicator():
    """
    Class with communication interface, that provide place for action.
    Communicator contains:
      - intput - communacion interface 
        (:class:`communication.communication.InputComm`) 
        for communacion with previous communicator
      - input - communacion interface 
        (:class:`communication.communication.OutputComm`) 
        for communacion with next communicator
      - function action_func_before, that is possible set by
        constructor, end is call before resending received data
        from next communicator 
      - function action_func_after, that is possible set by
        constructor, end is call before resending answer received 
        from previous communicator        
    """
    
    def __init__(self, init_conf, id=None , action_func_before=None, action_func_after=None):
        self.input = None
        """class for input communication"""
        self.id = id
        """Prefix that is added after log"""
        self.output = None
        """class for output communication"""
        self.next_communicator = init_conf.next_communicator
        """communicator file that will be start"""
        self.communicator_name = init_conf.communicator_name
        """this communicator name for login file, ..."""
        self.log_level = init_conf.log_level        
        """log level for communicator"""
        self._instaled = False        
        """if installation process of next communicator is finished"""
        self._install_lock = threading.Lock()
        """_installed lock"""
        self._instalation_begined = False
        """if installation begined"""
        self.stop = False
        """Stop processing of run function"""
        
        self._set_loger(Installation.get_result_dir_static(init_conf.mj_name), 
            self.communicator_name, self.log_level)
        if action_func_before is None:
            self.action_func_before = self.standart_action_funcion_before
        else:
            self.action_func_before = action_func_before
            """
            Function for processing of action in class above before sending message
            
            Parameter: Is received message object
            Return: tuple in two Booleans and message. First boolean if action is resend,
            second if is processed in standart way and if message is not None, is ressend
            without waiting for processing of communicator above
            """
        if action_func_after is None:
            self.action_func_after = self.standart_action_funcion_after
        else:
            self.action_func_after = action_func_after
            """
            Function for processing of action in class above after sending message

            Parameter: Is received message object
            Return: Message that is return or None
            """
        if init_conf.input_type == comconf.InputCommType.std:
            self.input =StdInputComm(sys.stdin, sys.stdout)
            self.input.connect()
        elif init_conf.input_type == comconf.InputCommType.pbs:
            self.input = PbsInputComm(init_conf.port)
            self.input.connect()
        elif init_conf.input_type == comconf.InputCommType.socket:
            self.input = SocketInputComm(init_conf.port)
            self.input.connect()
            
        init_conf.output_type
        
        if init_conf.output_type == comconf.OutputCommType.none:
            self.output = self.get_output(self, init_conf)
        else:
            self.output.set_install_params(init_conf.python_exec,  init_conf.scl_enable_exec)

    def get_output(self, conf):
        """Inicialize output using defined type"""
        output = None
        if conf.output_type == comconf.OutputCommType.ssh:
            output = SshOutputComm(conf.host, conf.mj_name, conf.uid, conf.pwd)
            output.connect()
        elif conf.output_type == comconf.OutputCommType.pbs:
            self.output = PbsOutputComm(conf.mj_name, conf.port, conf.pbs)            
        elif conf.output_type == comconf.OutputCommType.exec_:
            self.output = ExecOutputComm(conf.mj_name, conf.port)
        return output

    def _set_loger(self,  path, name, level):
        """set logger"""
        if self.id is None:
            log_file = os.path.join(path, "log_" + name +".log")
        else:
            log_file = os.path.join(path, "log_" + name + "_" + self.id + ".log")
        logging.basicConfig(filename=log_file,level=level, 
            format='%(asctime)s %(levelname)s %(message)s')
        logging.info("Application " + self.communicator_name + " is started")
   
    def  standart_action_funcion_before(self, message):
        """This function will be set by communicator. This is empty default implementation."""
        if message.action_type == tdata.ActionType.installation:
            if isinstance(self.output, ExecOutputComm) and \
                not isinstance(self.output, PbsOutputComm):
                self._instalation_begined = True
                logging.debug("Installation to local directory")
                self.install()
                return True, True, None
            else:
                if self._instalation_begined:
                    if self.is_installed():
                        logging.debug("Installation to remote directory ended")
                        return True, True, None
                    logging.debug("Installation in process signal was sent")
                else:
                    logging.debug("Installation to remote directory began")
                    self._instalation_begined = True
                    t = threading.Thread(target=self.install)
                    t.daemon = True
                    t.start()
                action = tdata.Action(tdata.ActionType.action_in_process)
                return False, False, action.get_message()
        return True, True, None
        
    def  standart_action_funcion_after(self, message,  response):
        """This function will be set by communicator. This is empty default implementation."""
        if message.action_type == tdata.ActionType.stop:
            if response is not None and \
                response.action_type == tdata.ActionType.action_in_process:
                return response
            logging.info("Stop signal is received")
            self.stop =True
            action = tdata.Action(tdata.ActionType.ok)
            return action.get_message()
        return None        
    
    def close(self):
        """Release resorces"""
        time.sleep(1)
        if self.output is not None:
            self.output.disconnect()
        time.sleep(1)
        if self.input is not None:
            self.input.disconnect()
        logging.info("Application " + self.communicator_name + " is stopped")
    
    def install(self):
        """make installation"""
        self.output.install()
        logging.debug("Run next file")
        self._exec_()
        self._install_lock.acquire()
        self._instaled = True
        self._install_lock.release()
        
    def is_installed(self):
        """if installation process of next communicator is finished"""
        self._install_lock.acquire()
        ret = self._instaled
        self._install_lock.release()
        return ret
        
    def _exec_(self):
        """run set python file"""
        self.output.exec_(self.next_communicator)
        if isinstance(self.output, ExecOutputComm):
            i=0
            while i<3:
                try:
                    self.output.connect()            
                    break
                except ConnectionRefusedError as err:
                    i += 1
                    time.sleep(1)
                    if i == 3:
                        logging.error("Connect error (" + str(err) + ')')
                except err:
                    logging.error("Connect error (" + str(err) + ')')
                    break
                    
    def run(self):
        """
        Infinite loop that is interupt by sending stop action by input,
        that send all messages to next communicator by standart
        way.
        
        1. receive message
        2. func self.action_func_before
        3. resend message to next communicator
        4. receve message from next communicator 
        5. func self.action_func_after
        6. answer
        
        Redefine self.action_func_before and self.action_func_after for
        advanced actions.
        Use send_action instead, if you want work in real time
        """
        self.stop = False
        while not self.stop:
            if self.input is None:
                logging.fatal("Infinite loop")
                raise Exception("Infinite loop")
                break
            message = self.input.receive(1)
            mess = None
            if message is not None:
                error = False
                logging.debug("Input message is receive (" + str(message) + ')')
                resend,  process, mess = self.action_func_before(message)
                if process:
                    action=tdata.Action(message.action_type,  message.json)
                    action.run
                if resend and self.output is not None:
                    logging.debug("Message is resent")
                    self.output.send(message)
                if resend and self.output is not None:
                    res = self.output.receive()
                    mess = res
                    logging.debug("Answer to resent message is receive (" + str(mess) + ')')
                mess_after = self.action_func_after(message, mess)
                if mess_after is not None:
                    mess = mess_after
                    logging.debug("Message after: (" + str(mess) + ')')
                if mess == None:
                    action=tdata.Action(tdata.ActionType.error)
                    if resend:
                        action.data.data["msg"] = "timeout"
                    else:
                        action.data.data["msg"] = "implementation error"
                    mess = action.get_message()
                    error = True
                self.input.send(mess)
                if error:
                    logging.error("Error answer sent (" + str(mess) + ')')
                else:
                    logging.debug("Answer is sent (" + str(mess) + ')')   

    def send_message(self, message):
        """send message to output"""
        self.output.send(message)
        logging.debug("Message is send (" + str(message) + ')')
       
    def send_long_action(self, action):
        """send message with long response time, to output"""
        sec = time.time() + LONG_MESSAGE_TIMEOUT
        while sec  > time.time() :
            message = action.get_message()
            self.send_message(message)
            mess = self.receive_message(120)
            if mess is None:
                break
            if mess.action_type != tdata.ActionType.action_in_process:
                return mess
        return None

    def receive_message(self, timeout=60):
        """receive message from output"""
        mess = self.output.receive(timeout)
        logging.debug("Answer to message is receive (" + str(mess) + ')')
        return mess    
