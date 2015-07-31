"""Class for communacion"""
import sys
import time
import logging
import os
import data.communicator_conf as comconf
import communication.communication as com
import data.transport_data as tdata
import data.installation as dinstall

class Communicator():
    """Communication class"""
    
    def __init__(self, init_conf, action_func=None):
        self.input = None
        """class for input communication"""
        self.output = None
        """class for output communication"""
        self.next_communicator = init_conf.next_communicator
        """communicator file that will be start"""
        self.sleep_interval = 5
        """interval for reading input (default 5 - 5s)"""
        self.communicator_name = init_conf.communicator_name
        """this communicator name for login file, ..."""
        self.log_level = init_conf.log_level        
        """log level for communicator"""
        self._set_loger(dinstall.Installation.get_result_dir(), 
            self.communicator_name, self.log_level)
        if action_func is None:
            self.action_func = self.standart_action_funcion
        else:
            self.action_func = action_func
            """
            Function for processing of action in class above
            
            Parameter: Is message object
            Return: tuple in two Booleans and message. First boolean if action is resend,
            second if is processed in standart way and if message is not None, is ressend
            without waiting for processing of communicator above
            """
        if init_conf.input_type == comconf.InputCommType.std:
            self.input = com.InputComm(sys.stdin, sys.stdout)
        if init_conf.output_type == comconf.OutputCommType.ssh:
            self.output = com.SshOutputComm(init_conf.host, init_conf.uid, init_conf.pwd)
            self.output.connect()
  
    def _set_loger(self,  path, name, level):
        """set logger"""
        log_file = os.path.join(path, "log_" + name +".log")
        logging.basicConfig(filename=log_file,level=level, 
            format='%(asctime)s %(levelname)s %(message)s')
   
    def  standart_action_funcion(self, message):
        """This function will be set by communicator. This is empty default implementation."""
        return True, True, None
    
    def close(self):
        """Release resorces"""
        if isinstance(self.output, com.SshOutputComm):
            self.output.disconnect()
    
    def install(self):
        """make installation"""
        self.output.install()
      
    def exec_(self):
        """run set python file"""
        self.output.exec_(self.next_communicator)
        
    def run(self):
        """
        Infinite loop that is interupt by sending stop action by input
        
        Use send_action instead, if you want work in real time
        """
        stop = False
        while True:
            if self.input is None:
                raise Exception("Infinite loop")
                break
            message = self.input.receive(0)
            if message is not None:
                error = False
                logging.debug("Input message is receive (" + str(message) + ')')
                if message.action_type == tdata.ActionType.stop:
                    stop=True
                resend,  process, mess = self.action_func(message)
                if process:
                    action=tdata.Action(message.action_type,  message.json_data)
                    action.run
                if resend and self.output is not None:
                    logging.debug("Message is resent")
                    self.output.send(message)
                if resend and mess is None:
                    mess = self.output.receive()
                    logging.debug("Answer to resent message is receive (" + str(mess) + ')')
                if mess == None:
                    action=tdata.Action(tdata.ActionType.error)
                    if resend:
                        action.action.data["msg"] = "timeout"
                    else:
                        action.data.data["msg"] = "implementation error"
                    mess = action.get_message()
                    error = True
                self.input.send(mess)
                if error:
                    logging.error("Error answer sent (" + str(mess) + ')')
                else:
                    logging.debug("Answer is sent (" + str(mess) + ')')
            if stop:
                break
            time.sleep(self.sleep_interval)                        

    def send_message(self, message):
        """send message to output"""
        self.output.send(message)
        logging.debug("Message is send (" + str(message) + ')')

    def receive_message(self):
        """receive message from output"""
        mess = self.output.receive()
        logging.debug("Answer to message is receive (" + str(mess) + ')')
        return mess 
