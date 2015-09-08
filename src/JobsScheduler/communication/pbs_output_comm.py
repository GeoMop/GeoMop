import logging
import subprocess
import re
import helpers.pbs as pbs
import time
from communication.exec_output_comm import ExecOutputComm

class PbsOutputComm(ExecOutputComm):
    """Communication over PBS"""
    
    def __init__(self, port, pbs_config):
        super(PbsOutputComm, self).__init__(port)
        self.config = pbs_config
        """pbs configuration (:class:`data.communicator_conf.PbsConfig`) """
        self.jobid = None
        """Id for job identification"""
        
    def exec_(self, python_file):
        """run set python file in ssh"""
        hlp = pbs.Pbs(self.config) 
        hlp.prepare_file(self.installation.get_command_only(python_file), self.installation.get_interpreter())      
        process = subprocess.Popen(hlp.get_qsub_args(), 
            stdout=subprocess.PIPE)
        # wait for jobid
        out = process.stdout.readline()
        job  = re.match( '(\d+)', str(out, 'utf-8'))
        if job is not None:
            self.jobid  =  int(job.group(1))
            logging.debug("Job is queued (id:" + job.group(1) + ")")
            if self.config.with_socket:
                i = 0
                while(i<1800):
                    lines = hlp.get_outpup()
                    time.sleep(1)
                    if lines is not None and len(lines) >= 2:
                        lines = hlp.get_outpup()
                        break
                    i += 1
                host = re.match( 'HOST:--(\d+)--',  lines[0])
                if host is not None:
                    logging.debug("Next communicator return socket host:" + host.group(1)) 
                    self.host = host.group(1)
                port = re.match( 'PORT:--(\d+)--', lines[1])
                if port is not None:
                    logging.debug("Next communicator return socket port:" + port.group(1)) 
                    self.port = int(port.group(1))

         
    def connect(self):
        """connect session"""
        if self.config.with_socket:
            super(PbsOutputComm, self).connect()
         
    def disconnect(self):
        """disconnect session"""
        if self.config.with_socket:
            super(PbsOutputComm, self).diconnect()
        hlp = pbs.Pbs(self.config) 
        error = hlp.get_errors()
        logging.warning("Error output contains error:" + error) 
        
    def send(self,  mess):
        """send json message"""        
        if self.config.with_socket:
            super(PbsOutputComm, self).send(mess)

    def receive(self, timeout=60):
        """receive json message"""
        if self.config.with_socket:
            return super(PbsOutputComm, self).receive(timeout)
