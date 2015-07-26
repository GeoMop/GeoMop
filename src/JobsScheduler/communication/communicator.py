"""Class for communacion"""
import sys
import time
import data.communicator_conf as comconf
import communication.communication as com

class Communicator():
    """Communication class"""
    
    def __init__(self, init_conf):
        self.input = None
        """class for input communication"""
        self.output = None
        """class for output communication"""
        self.install_path=None
        """path where is copied files"""
        self.sleep_interval = 5
        """interval for reading input (default 5 - 5s)"""
        if init_conf.input_type == comconf.InputCommType.std:
            self.input = com.InputComm(sys.stdin, sys.stdin)
        if init_conf.output_type == comconf.OutputCommType.ssh:
            self.input = com.SshOutputComm(init_conf.uid, init_conf.pwd)
    
    def run(self):
        """
        Infinite loop that is interupt by sending stop action by input
        
        Use send_action instead, if you want work in real time
        """
        while True:
            if self.input is None:
                raise Exception("Infinite loop")
                break
            
            time.sleep(self.sleep_interval)
                        

    def send_action(self, action):
        """send action"""
