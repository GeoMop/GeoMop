"""Class for communacion"""
import sys
import logging
import os
import time
import threading
import data.communicator_conf as comconf
import communication.communication as com
import data.transport_data as tdata
import data.installation as dinstall

class Communicator():
    """
    Class with communication interface, that provide place for action.
    Communicator contains:
      - intput - communacion interface 
        (:class:`communication.communicationa.InputComm`) 
        for communacion with previous communicator
      - input - communacion interface 
        (:class:`communication.communicationa.OutputComm`) 
        for communacion with next communicator
      - function action_func_before, that is possible set by
        constructor, end is call before resending received data
        from next communicator 
      - function action_func_after, that is possible set by
        constructor, end is call before resending answer received 
        from previous communicator        
    """
    
    def __init__(self, init_conf, action_func_before=None, action_func_after=None):
        self.input = None
        """class for input communication"""
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
        self._set_loger(dinstall.Installation.get_result_dir(), 
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
            self.input = com.StdInputComm(sys.stdin, sys.stdout)
            self.input.connect()
        elif init_conf.input_type == comconf.InputCommType.socket:
            self.input = com. SocketInputComm(init_conf.port)
            self.input.connect()
            
        if init_conf.output_type == comconf.OutputCommType.ssh:
            self.output = com.SshOutputComm(init_conf.host, init_conf.uid, init_conf.pwd)
            self.output.connect()
        elif init_conf.output_type == comconf.OutputCommType.exec_:
            self.output = com. ExecOutputComm(init_conf.port)
  
    def _set_loger(self,  path, name, level):
        """set logger"""
        log_file = os.path.join(path, "log_" + name +".log")
        logging.basicConfig(filename=log_file,level=level, 
            format='%(asctime)s %(levelname)s %(message)s')
        logging.info("Application " + self.communicator_name + " is started")
   
    def  standart_action_funcion_before(self, message):
        """This function will be set by communicator. This is empty default implementation."""
        if message.action_type == tdata.ActionType.installation:
            if isinstance(self.output, com.ExecOutputComm):
                self._instalation_begined = True
                logging.debug("Installation to local directory")
                self.install()
                logging.debug("Run next file")
                self.exec_()
                action = tdata.Action(tdata.ActionType.ok)
                return True, True, None
            else:
                if self._instalation_begined:
                    if self.is_installed():
                        logging.debug("Installation to remote directory ended")
                        self.exec_()
                        return True, True, None
                    logging.debug("Installation in process signal was sent")
                else:
                    logging.debug("Installation to remote directory began")
                    self._instalation_begined = True
                    t = threading.Thread(target=self.install)
                    t.daemon = True
                    t.start()
                action = tdata.Action(tdata.ActionType.installation_in_process)
                return False, False, action
        return True, True, None
        
    def  standart_action_funcion_after(self, message):
        """This function will be set by communicator. This is empty default implementation."""
        return None
    
    def close(self):
        """Release resorces"""
        if self.output is not None:
            self.output.disconnect()
        if self.input is not None:
            self.input.disconnect()
        logging.info("Application " + self.communicator_name + " is stopped")
    
    def install(self):
        """make installation"""
        self.output.install()
        self._install_lock.acquire()
        self._instaled = True
        self._install_lock.release()
        
    def is_installed(self):
        """if installation process of next communicator is finished"""
        self._install_lock.acquire()
        ret = self._instaled
        self._install_lock.release()
        return ret
        
    def exec_(self):
        """run set python file"""
        self.output.exec_(self.next_communicator)
        if isinstance(self.output, com.ExecOutputComm):
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
        Infinite loop that is interupt by sending stop action by input
        
        Use send_action instead, if you want work in real time
        """
        stop = False
        while True:
            if self.input is None:
                logging.fatal("Infinite loop")
                raise Exception("Infinite loop")
                break
            message = self.input.receive(1)
            if message is not None:
                error = False
                logging.debug("Input message is receive (" + str(message) + ')')
                if message.action_type == tdata.ActionType.stop:
                    logging.info("Stop signal is received")
                    stop=True
                resend,  process, mess = self.action_func_before(message)
                if process:
                    action=tdata.Action(message.action_type,  message.json)
                    action.run
                if resend and self.output is not None:
                    logging.debug("Message is resent")
                    self.output.send(message)
                if resend and self.output is not None:
                    res = self.output.receive()
                    if mess is None:
                        mess = res
                    logging.debug("Answer to resent message is receive (" + str(mess) + ')')
                mess_after = self.action_func_after(message)
                if mess_after is not None:
                    mess = mess_after
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

    def send_message(self, message):
        """send message to output"""
        self.output.send(message)
        logging.debug("Message is send (" + str(message) + ')')

    def receive_message(self):
        """receive message from output"""
        mess = self.output.receive()
        logging.debug("Answer to message is receive (" + str(mess) + ')')
        return mess    
