"""Class for communacion"""
import sys
import time
import data.communicator_conf as comconf
import communication.communication as com
import data.transport_data as tdata 

class Communicator():
    """Communication class"""
    
    def __init__(self, init_conf, action_func=None):
        self.input = None
        """class for input communication"""
        self.output = None
        """class for output communication"""
        self.install_path=None
        """path where is copied files"""
        self.sleep_interval = 5
        """interval for reading input (default 5 - 5s)"""
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
            self.input = com.InputComm(sys.stdin, sys.stdin)
        if init_conf.output_type == comconf.OutputCommType.ssh:
            self.output = com.SshOutputComm(init_conf.uid, init_conf.pwd)
            self.output.connect()
    
    def  standart_action_funcion(self, message):
        return True, True, None
    
    def close(self):
        """Release resorces"""
        if isinstance(self.output, com.SshOutputComm):
            self.output.disconnect()
    
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
            message = self.input.receive()
            if message is not None:
                if message.action_type == tdata.ActionType.stop:
                    stop=True
                resend,  process, mess = self.action_func(message)
                if process:
                    action=tdata.Action(message.action_type,  message.json_data)
                    action.run
                if resend and self.output is not None:
                    self.output.send(message)
                if resend and mess is None:
                    mess = self.output.receive()
                if mess == None:
                    action=tdata.Action(tdata.ActionType.error)
                    if resend:
                        action.action.data["msg"] = "timeout"
                    else:
                        action.data.data["msg"] = "implementation error"
                    mess = action.get_message()
                self.input.send_mess()
            if stop:
                break
            time.sleep(self.sleep_interval)
                        

    def send_message(self, action):
        """send action"""
        message = action.get_message()
        self.output.send_mess(message)
        return action.get_message()
