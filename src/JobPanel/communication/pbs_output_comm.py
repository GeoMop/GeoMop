import logging
import subprocess
import re
from JobPanel.helpers import pbs
import time
import copy
import sys
from .exec_output_comm import ExecOutputComm

logger = logging.getLogger("Remote")

class PbsOutputComm(ExecOutputComm):
    """Communication over PBS"""
    
    def __init__(self, mj_name, an_name, port, pbs_config):
        super(PbsOutputComm, self).__init__(mj_name, an_name, port)
        self.config = copy.deepcopy(pbs_config)
        """pbs configuration (:class:`data.communicator_conf.PbsConfig`) """
        self.jobid = None
        """Id for job identification"""
        self.node = None
        """Name of node"""

    def exec_(self, python_file, mj_id):
        """run set python file in ssh"""
        self.installation.local_copy_path()
        hlp = pbs.Pbs(self.installation.get_mj_data_dir(), self.config)        
        hlp.prepare_file(self.installation.get_command_only(python_file, mj_id),
                                  self.installation.get_interpreter(), 
                                  self.installation.get_prepare_pbs_env()  
                                 )
        logger.debug("Qsub params: " + str(hlp.get_qsub_args()))
        si = None 
        if sys.platform == "win32":
            si = subprocess.STARTUPINFO()
            si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        process = subprocess.Popen(hlp.get_qsub_args(), 
                        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, startupinfo=si)
        return_code = process.poll()
        if return_code is not None:
            raise Exception("Can not start next communicator " + python_file + 
                " (return code: " + str(return_code) + ")")    
        # wait for jobid
        out = process.stdout.readline()
        job  = re.match( '(\S+)', str(out, 'utf-8'))
        if job is not None:
            try:
                self.jobid  =  int(job.group(1))
            except ValueError:
                jobid = re.match( '(\d+)\.', job.group(1))
                if jobid is not None:
                    self.jobid = int(jobid.group(1))
            logger.debug("Job is queued (id:" + str(self.jobid) + ")")            
            if self.config.with_socket:                
                i = 0
                while(i<1800):
                    lines = hlp.get_outpup()
                    time.sleep(1)
                    if lines is not None and len(lines) >= 2:
                        lines = hlp.get_outpup()
                        break
                    i += 1
                self._set_node()
                host = re.match( 'HOST:--(\S+)--',  lines[0])
                if host is not None:
                    logger.debug("Next communicator return socket host:" + host.group(1)) 
                    self.host = host.group(1)
                else:
                    # try node                    
                    if self.node is not None:
                        self.host = self.node
                port = re.match( 'PORT:--(\d+)--', lines[1])
                if port is not None:
                    logger.debug("Next communicator return socket port:" + port.group(1)) 
                    self.port = int(port.group(1))
        self.initialized=True
        
    def _set_node(self):
        """try set first node"""
        i=0
        while True and i<300:
            self.node = None
            logger.debug( "Command:" + "qstat -n " + str(self.jobid))
            si = None 
            if sys.platform == "win32":
                si = subprocess.STARTUPINFO()
                si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            process = subprocess.Popen(["qstat", "-n", str(self.jobid)], 
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, startupinfo=si)
            return_code = process.wait()
            if return_code is not None and return_code==0:
                while True:
                    line = str(process.stdout.readline(), 'utf-8')
                    logger.debug("line: " + line)
                    if line != '':
                        node=line
                    else:
                        break
                self.node = node.strip()
                if len(self.node)==0 or " " in self.node:
                    logger.debug("Bad node:" + node) 
                    self.node = None
                else:
                    logger.debug("Node is:" + self.node) 
            else:
                logger.debug("return code is:" + str(return_code))                
            i += 1
            # if self.node is "--", node information is not ready 
            if self.node is None or self.node != "--":
                break
            time.sleep(3)

    def is_running_next(self):
        """
        Return if next communicator run
        """
        # TODO QSTAT task
        return False
        
    def kill_next(self):
        """
        kill next communicator
        """
        if self.is_running_next():
            # TODO QDEL task
            pass

    def connect(self):
        """connect session"""
        if self.config.with_socket:
            super(PbsOutputComm, self).connect()

    def disconnect(self):
        """disconnect session"""
        if self.config.with_socket:
            super(PbsOutputComm, self).disconnect()
        hlp = pbs.Pbs(self.installation.get_mj_data_dir(),self.config) 
        error = hlp.get_errors()
        if error is not None:
            logger.warning("Error output contains error:" + error)
        if not self.config.with_socket:
            self.installation.unlock_application(self.installation.mj_name, self.installation.an_name)
        
    def send(self,  mess):
        """send json message"""        
        if self.config.with_socket:
            super(PbsOutputComm, self).send(mess)
            

    def receive(self, timeout=60):
        """receive json message"""
        if self.config.with_socket:
            return super(PbsOutputComm, self).receive(timeout)
