"""Class for communacion"""
import sys
import logging
import os
import time
import threading
import re

import data.communicator_conf as comconf
import data.transport_data as tdata
from data.user_helper import Users
from data.communicator_status import CommunicatorStatus
from communication.std_input_comm import StdInputComm
from  communication.socket_input_comm import SocketInputComm
from  communication.ssh_output_comm import SshOutputComm
from  communication.ssh_output_tunnel_comm import SshOutputTunnelComm
from  communication.exec_output_comm import  ExecOutputComm
from  communication.installation import Installation
from  communication.pbs_output_comm import PbsOutputComm
from  communication.pbs_input_comm import PbsInputComm
from data.states import TaskStatus

LONG_MESSAGE_TIMEOUT=600
__NOT_INSTALLED__ = "Next communicator was not installed"
__TIMEOUT__ = "Communication timeout is exceed"
logger = logging.getLogger("Remote")

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
    def __init__(self, init_conf, id=None , action_func_before=None, action_func_after=None, idle_func=None):
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
        self._tunneled = False        
        """if is tunneled connecting to next next communicator"""
        self._restored = False        
        """if restored process is finished"""
        self.instalation_fails_mess = None        
        """
        if installation fail, this variable contain instalation message,
        that is send.
        """
        self._install_lock = threading.Lock()
        """_installed lock"""
        self._download_processed = tdata.ProcessType.ready        
        """Download of result files is processed"""
        self._download_processed_lock = threading.Lock()
        """_download_processed lock"""
        self._instalation_begined = False
        """if installation begined"""
        self._tunnelation_begined = False
        """if tunnelation begined"""
        self._get_port_finished = False
        """if try gain port is finished"""
        self._tunnelation_port = None
        """tunnelation port"""
        self._tunnelation_host = None
        """tunnelation host"""
        self.stop = False
        """Stop processing of run function"""
        self.mj_name = init_conf.mj_name
        """folder name for multijob data"""
        self.an_name = init_conf.an_name
        """folder name for analyzis data"""
        self.python_env = init_conf.python_env
        """python running envirounment"""
        self.libs_env = init_conf.libs_env
        """libraries running envirounment"""
        self._interupt = False
        """interupt connections after message sending"""
        Installation.set_env_params(init_conf.python_env,  init_conf.libs_env, init_conf.paths_config)  
        
        self.status = None
        self._load_status() 
        """Persistent communicator data"""
        self._set_loger(Installation.get_result_dir_static(init_conf.mj_name, init_conf.an_name), 
            self.communicator_name, self.log_level, init_conf.central_log)
        if action_func_before is None:
            self.action_func_before = self.standart_action_function_before
        else:
            self.action_func_before = action_func_before
            """
            Function for processing of action in class above before sending message
            
            Parameter: Is received message object
            Return: tuple in Boolean and message. Boolean is True if action is 
            resend to next communicator and if message is not None is send back
            instead one returned by resend  
            """
        if action_func_after is None:
            self.action_func_after = self.standart_action_function_after
        else:
            self.action_func_after = action_func_after
            """
            Function for processing of action in class above after sending message

            Parameter: Is received message object
            Return: Message that is return or None
            """
        if idle_func is None:
            self.idle_func = self.standart_idle_function
        else:
            self.idle_func = idle_func
            """
            Function for processing some code in iddle time 
            during run function processing.
            
            All code processed in this function should take a small time intervall,
            if a long action is requared, use thread.
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
            if init_conf.output_type == comconf.OutputCommType.exec_:
                time.sleep(2)
        if init_conf.output_type != comconf.OutputCommType.none:
            self.output = self.get_output(init_conf, self.mj_name, self.an_name)
            
    @staticmethod
    def get_output(conf, mj_name, an_name, new_name=None):
        """Inicialize output using defined type"""
        output = None
        if conf.output_type == comconf.OutputCommType.ssh or \
            conf.output_type == comconf.OutputCommType.ssh_tunnel:
            home_dir = None
            if conf.paths_config is not None:
                home_dir = conf.paths_config.home_dir
            dir = Installation.get_mj_data_dir_static(mj_name, an_name)
            u = Users(conf.ssh.name, dir, home_dir, conf.ssh.to_pc,  conf.ssh.to_remote)
            pwd = u.get_login(conf.ssh.pwd, conf.ssh.key,conf.conf_long_id)
            if conf.output_type == comconf.OutputCommType.ssh:
                output = SshOutputComm(conf.ssh.host, conf.mj_name, conf.an_name, conf.ssh.uid,pwd)
            else:
                output = SshOutputTunnelComm(conf.ssh.host, conf.port, conf.mj_name, conf.an_name, conf.ssh.uid,pwd)
            output.connect()
        elif conf.output_type == comconf.OutputCommType.pbs:
            old_name = conf.pbs.name
            if new_name is not None:
                conf.pbs.name = new_name
            output = PbsOutputComm(conf.mj_name, conf.an_name, conf.port, conf.pbs)
            conf.pbs.name = old_name
        elif conf.output_type == comconf.OutputCommType.exec_:
            output = ExecOutputComm(conf.mj_name, conf.an_name, conf.port)        
        output.set_version_params(conf.app_version,  conf.conf_long_id) 
        return output
        
    def _load_status(self):
        """load status"""
        name = self.communicator_name
        if self.id is not None:
            name += "_" + self.id
        self.status = CommunicatorStatus(
            Installation.get_status_dir_static(self.mj_name, self.an_name), name) 
        self.status.load()

    def _set_loger(self,  path, name, level, central_log):
        """set logger"""
        if central_log:
            logger = logging.getLogger("Remote")
            if len(logger.handlers)>0:
                if logger.level>level:
                    logger.setLevel(level)
                    logger.handlers[0].setLevel(level)
                return
            dir = Installation.get_central_log_dir_static()
            if not os.path.isdir(dir):
                return
            log_file = os.path.join(dir, "app-centrall.log")
        else:
            log_path = os.path.join(path, "log")
            if not os.path.isdir(log_path):
                try:
                    os.makedirs(log_path)
                except:
                    log_path = path
            if self.id is None:
                log_file = os.path.join(log_path, name +".log")
            else:
                log_file = os.path.join(log_path, name + "_" + self.id + ".log")            
            logger = logging.getLogger("Remote")
        logger.setLevel(level)

        fh = logging.FileHandler(log_file)
        fh.setLevel(level)

        formatter = logging.Formatter(
            '%(asctime)s %(levelname)s %(message)s')

        fh.setFormatter(formatter)
        logger.addHandler(fh)    
        logger.info("Application " + self.communicator_name + " is started")
   
    def  standart_idle_function(self):
        """This function will be call, if meesage is not receive in run function."""
        time.sleep(0.5)
   
    def  standart_action_function_before(self, message):
        """This function will be set by communicator. This is empty default implementation."""
        if message.action_type == tdata.ActionType.ping:
            #action will be processed in after funcion
            return False, None
        if message.action_type == tdata.ActionType.redirect_socket_conn:
            if not isinstance(self.output, ExecOutputComm):
                action=tdata.Action(tdata.ActionType.error)
                action.data.data["msg"] = "Input type is not support socket connection"
                action.data.data["severity"] = 5 
                logger.error("Unsupported message redirect_socket_conn")                
            else:
                action=tdata.Action(tdata.ActionType.socket_conn)
                action.data.set_conn(self.output.host, str(self.output.port))
                self._interupt = True
            return False, action.get_message()
        if message.action_type == tdata.ActionType.destroy:
            self._destroy()
        if message.action_type == tdata.ActionType.restore_connection or \
            message.action_type == tdata.ActionType.restore:
            if not self._restored:
                res = self.restore(message.action_type == tdata.ActionType.restore)
                if res is not None:
                    # restore retur error
                    action=tdata.Action(tdata.ActionType.error)
                    action.data.data["msg"] = res
                    action.data.data["severity"] = 5
                    if self.status.next_started:
                        action.data.data["severity"] = 3
                    return False, action.get_message()
                #restore only one communicator per request
                action = tdata.Action(tdata.ActionType.action_in_process)
                return False, action.get_message()
        if message.action_type == tdata.ActionType.installation:
            if self._tunnelation_begined:
                self._install_lock.acquire()
                get_port_finished = self._get_port_finished
                self._install_lock.release()
                if not get_port_finished:
                    self._get_tunnel_addres()                    
                    action = tdata.Action(tdata.ActionType.install_in_process)
                    return False, action.get_message()                    
                self._install_lock.acquire()
                tunneled = self._tunneled
                self._install_lock.release()
                if not tunneled:
                    action = tdata.Action(tdata.ActionType.install_in_process)
                    return False, action.get_message()
                return True, None
            if self.is_installed() and self.instalation_fails_mess is not None:
                action=tdata.Action(tdata.ActionType.error)
                action.data.data["msg"] = self.instalation_fails_mess
                action.data.data["severity"] = 5 
                return False, action.get_message()
            if isinstance(self.output, ExecOutputComm) and \
                not isinstance(self.output, PbsOutputComm) and \
                not self.libs_env.install_job_libs:
                if not self.is_installed():
                    self._instalation_begined = True
                    logger.debug("Installation to local directory")
                    self.install()
                return True, None
            else:
                if self._instalation_begined:
                    if self.is_installed():
                        return True, None
                    logger.debug("Installation in process signal was sent")
                else:
                    logger.debug("Installation to remote directory began")
                    self._instalation_begined = True
                    t = threading.Thread(target=self.install)
                    t.daemon = True
                    t.start()
                action = tdata.Action(tdata.ActionType.install_in_process)
                if isinstance(self.output, PbsOutputComm):
                    action.data.data['phase'] = TaskStatus.queued.value
                return False, action.get_message()
        if message.action_type == tdata.ActionType.download_res:
            if isinstance(self.output, SshOutputComm):
                processed = False
                self._download_processed_lock.acquire()
                if self._download_processed == tdata.ProcessType.processed:
                    processed = True
                self._download_processed_lock.release()
                if processed:
                    #action will be processed in after funcion
                    return False, None
        return True, None
        
    def  standart_action_function_after(self, message,  response):
        """This function will be set by communicator. This is empty default implementation."""
        if message.action_type == tdata.ActionType.installation and \
            isinstance(self.output, SshOutputTunnelComm):
            if response.action_type == tdata.ActionType.ok:
                self._tunnelation_begined = True
                t = threading.Thread(target=self.tunnel)
                t.daemon = True
                t.start()                
                action = tdata.Action(tdata.ActionType.action_in_process)
                return action.get_message()
        if message.action_type == tdata.ActionType.ping:
            action = tdata.Action(tdata.ActionType.ping_response)
            return action.get_message()
        if message.action_type == tdata.ActionType.interupt_connection:
            self._interupt = True
            action = tdata.Action(tdata.ActionType.ok)
            return action.get_message()
        if message.action_type == tdata.ActionType.stop or message.action_type == tdata.ActionType.delete:
            if response is not None and \
                response.action_type == tdata.ActionType.action_in_process:
                return response
            self.status.next_started = False
            self.status.save()
            if message.action_type != tdata.ActionType.delete:
                self.status.save()
                logger.info("Stop signal is received")
            else:
                self.delete()
                logger.info("Delete signal is received")
            if (response is None or \
                response.action_type != tdata.ActionType.ok) and \
                self.status.next_installed:
                self.terminate_connections()
            self.stop =True
            action = tdata.Action(tdata.ActionType.ok)
            return action.get_message()
        if message.action_type == tdata.ActionType.download_res:
            if response is None or \
                response.action_type != tdata.ActionType.action_in_process:
                # waiting to the next communicator is not needed
                if isinstance(self.output, SshOutputComm):
                    processed = False
                    start = False
                    self._download_processed_lock.acquire()
                    if self._download_processed == tdata.ProcessType.ready:
                        processed = True
                        start = True
                        self._download_processed = tdata.ProcessType.processed
                    elif self._download_processed == tdata.ProcessType.processed:
                        processed = True
                    else:
                        self._download_processed = tdata.ProcessType.ready
                    self._download_processed_lock.release()    
                    if start:
                        t = threading.Thread(target=self.download)
                        t.daemon = True
                        t.start()
                    if processed:
                        action = tdata.Action(tdata.ActionType.action_in_process)
                        return action.get_message()
                    action = tdata.Action(tdata.ActionType.ok)
                    return action.get_message()
                else:
                    self.download()
                    self._download_processed = tdata.ProcessType.ready
                    action = tdata.Action(tdata.ActionType.ok)
                    return action.get_message()
        return None    
    
    def restore(self, recreate=False):
        """Restore connection chain to next communicator"""
        self.status.load()
        if not self.status.next_installed:
            logger.info(__NOT_INSTALLED__)
            return __NOT_INSTALLED__
        if not self.status.next_started and not recreate:
            return "Next communicator was stopped"        
        if self.input is not None:
            self.input.load_state(self.status)
        if self.output is not None:
            self.output.load_state(self.status)
        if self.output is not None:
            if isinstance(self.output, SshOutputComm):
                try:
                    self.output.connect()
                    self.output.exec_(self.next_communicator, self.id)
                except Exception as err:
                    return "Can't create ssh connection ({0})".format(str(err))
            elif not self.output.isconnected():
                if recreate:
                    try:
                        self.output.exec_(self.next_communicator, self.id)
                    except Exception as err:
                        return "Can't create communicator ({0})".format(str(err))
                    if not self._connect_socket(self.output):
                        return "Can't recreate to next communicator"
                else:
                    if not self._connect_socket(self.output):
                        return "Can't connect to next communicator"
        self.status.interupted=False
        self.status.save()
        self._restored = True
        logger.info("Application " + self.communicator_name + " is restored")
        return None
        
    def interupt(self):
        """Interupt connection chain to next communicator"""
        self.status.interupted=True
        if self.input is not None:
            self.input.save_state(self.status)
        if self.output is not None:
            self.output.save_state(self.status)
        self.status.save()        
        if self.input is not None:
            if isinstance(self.input, StdInputComm):
                self.stop =True
            else:
                time.sleep(10)
                self.input.connect()
                self.close()
        else:
            #app
            self.close()
        logger.info("Application " + self.communicator_name + " is interupted")
    
    def close(self):
        """Release resorces"""
        time.sleep(1)
        if self.output is not None:
            self.output.disconnect()
            if not isinstance(self.output, SshOutputComm):
                self.delete_connection()
        time.sleep(1)
        if self.input is not None:
            self.input.disconnect()
            if isinstance(self.input, StdInputComm):
                Installation.unlock_application(self.mj_name, self.an_name)
        logger.info("Connection to application " + self.communicator_name + " is stopped")
    
    def install(self, unlock=True):
        """make installation"""
        if self.libs_env.install_job_libs:
            self.output.install_job_libs()
        self.output.install()
        self.instalation_fails_mess = self.output.get_instalation_fails_mess()
        if self.instalation_fails_mess is None:
            self.status.next_installed = True
            self.status.save()
            logger.debug("Run next file")
            self._exec_()
            self.status.next_started = True
            self.status.save()
        if unlock:
            self._install_lock.acquire()
            self._instaled = True
            self._install_lock.release()
            
    def _get_tunnel_addres(self):
        """Find out socket port and host from next communicator for tunneling"""
        action=tdata.Action(tdata.ActionType.redirect_socket_conn)
        mess = action.get_message()
        self.send_message(mess)
        mess = self.receive_message()
        if mess is not None and mess.action_type == tdata.ActionType.socket_conn:           
            self._tunnelation_host = mess.get_action().data.data['host']
            self._tunnelation_port = mess.get_action().data.data['port']
        self._install_lock.acquire()
        self._get_port_finished = True
        self._install_lock.release()
        
    def local_tunnel(self):
        """make ssh tunel synchrony on local computer"""
        if isinstance(self.output, SshOutputTunnelComm):
            self._get_tunnel_addres()
            self.tunnel()
            
    def tunnel(self):
        """make ssh tunnel"""
        while(True):
            self._install_lock.acquire()
            get_port_finished = self._get_port_finished
            self._install_lock.release()
            if get_port_finished:
                break
            time.sleep(0.5)
        self.output.create_tunnel(self._tunnelation_port, self._tunnelation_host)
        self._install_lock.acquire()
        self._tunneled = True
        self._install_lock.release()
        
    def download(self):
        """download result files"""
        logger.debug("Start downloading result files")
        res = self.output.download_result()
        logger.debug("End downloading result files")
        self._download_processed_lock.acquire()
        self._download_processed = tdata.ProcessType.finished
        self._download_processed_lock.release()
        return res
    
    def is_next_installed(self):
        """return if next communicator is inicialized"""
        return self.status.next_installed

    def delete(self):
        """
        delete data dir 
        
        - status data is deleted, communicator should be stopped afterwards
        - data is deleted only for ssh connection
        """
        if self.input is not None and \
            isinstance(self.input, StdInputComm):
            self.output.delete()
        
    def is_installed(self):
        """if installation process of next communicator is finished"""
        self._install_lock.acquire()
        ret = self._instaled
        self._install_lock.release()
        return ret
        
    def _exec_(self):
        """run set python file"""
        try:
            self.output.exec_(self.next_communicator, self.id)
        except Exception as err:
            logger.error(str(err))
            self.instalation_fails_mess = str(err)
        else:
            if not self._connect_socket(self.output):
                self.instalation_fails_mess = "Connection to next communicator fails"
            else:
                if not isinstance(self.output, SshOutputComm):
                    self.save_connection(self.output.host, self.output.port)
        if self.output is not None:
            self.output.save_state(self.status)
        self.status.save()
    
    @staticmethod
    def _connect_socket(output,  repeat=3):
        """connect to output socket"""
        if isinstance(output, ExecOutputComm):
            i=0
            while i<repeat:
                try:
                    output.connect()                    
                    return True
                except ConnectionRefusedError as err:
                    i += 1
                    time.sleep(1)
                    if i == repeat:
                        logger.error("Connect error (" + str(err) + ')')
                except err:
                    logger.error("Connect error (" + str(err) + ')')
                    break
            return False
        return True

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
                logger.fatal("Infinite loop")
                raise Exception("Infinite loop")
                break
            message = self.input.receive(0.1)
            mess = None
            if message is not None:
                error = False
                logger.debug("Input message is receive (" + str(message) + ')')
                resend, mess = self.action_func_before(message)
                if resend and self.output is not None:
                    logger.debug("Message is resent")
                    self.output.send(message)
                    mess = self.output.receive()
                    logger.debug("Answer to resent message is receive (" + str(mess) + ')')
                mess_after = self.action_func_after(message, mess)
                if mess_after is not None:
                    mess = mess_after
                    logger.debug("Message after: (" + str(mess) + ')')
                if mess == None:
                    action=tdata.Action(tdata.ActionType.error)
                    if resend:
                        action.data.data["msg"] = "timeout"
                    else:
                        action.data.data["msg"] = "implementation error"
                        action.data.data["severity"] = 3 
                    mess = action.get_message()
                    error = True
                self.input.send(mess)
                if error:
                    logger.error("Error answer was send (" + str(mess) + ')')
                else:
                    logger.debug("Answer was send (" + str(mess) + ')')   
            else:
                if self.is_installed():
                    self.idle_func()
            if self._interupt:
                self.interupt()
                self._interupt = False

    def send_message(self, message):
        """send message to output"""
        self.output.send(message)
        logger.debug("Message is send (" + str(message) + ')')
       
    def send_long_action(self, action):
        """send message with long response time, to output"""
        sec = time.time() + LONG_MESSAGE_TIMEOUT
        i = 0
        while sec  > time.time() :
            message = action.get_message()
            self.send_message(message)
            mess = self.receive_message(120)
            i += 1
            if i > 5:
                time.sleep(1)
            elif i > 20:
                time.sleep(5)
            elif i > 30:
                time.sleep(10)
            if mess is None:
                break
            if mess.action_type != tdata.ActionType.action_in_process:
                return mess
        action=tdata.Action(tdata.ActionType.error)
        action.data.data["msg"] = __TIMEOUT__
        mess = action.get_message()
        return mess
        
    def receive_message(self, timeout=60):
        """receive message from output"""
        mess = self.output.receive(timeout)
        logger.debug("Answer to message is receive (" + str(mess) + ')')
        return mess    

    def lock_installation(self):
        """Set installation locks, return if should installation continue"""
        self.output.lock_installation()
        
    def unlock_installation(self):
        """Unset installation locks"""
        self.output.unlock_installation()
    
    @staticmethod    
    def unlock_application(mj_name, an_name):
        """Unset application locks"""
        Installation.unlock_application(mj_name, an_name)
    
    def save_connection(self, host, port, id=None):
        """Save connection for possible termination"""
        id = str(id)
        file = os.path.join( Installation.get_status_dir_static(self.mj_name, self.an_name), "conn_"+id) 
        with open(file, 'w') as f:
            f.write("HOST:--" + str(host) + "--\n")
            f.write("PORT:--" + str(port) + "--\n")    
 
        
    def delete_connection(self, id=None):
        """delete file with connection"""
        id = str(id)
        file = os.path.join( Installation.get_status_dir_static(self.mj_name, self.an_name), "conn_"+id)
        if os.path.isfile(file):
            os.remove(file) 
            
    def terminate_connections(self):
        """
        send terminate message to all recorded connections, and delete connections files
        
        After all function try kill next communicator (if next communicator is exec and was restored
        killing fails, but previous action should be functional - restore is possible only for active 
        connections)
        """
        dir = Installation.get_status_dir_static(self.mj_name, self.an_name)
        logger.info("Comunicator start destroying process")
        for root, dirs, files in os.walk(dir):
            for name in files:
                if name[:5]=="conn_":
                    file = os.path.join(root, name)
                    lines = []
                    with open(file, 'w') as f:
                        lines = f.readlines()
                    if len(lines)>1:
                        host = re.match( 'HOST:--(\S+)--',  lines[0])
                        if host is not None:
                            host = host.group(1)
                            port = re.match( 'PORT:--(\d+)--', lines[1])
                            if port is not None:
                                self.port = int(port.group(1))
                                try:
                                    conn = ExecOutputComm(self.mj_name, port)
                                    conn.host = host
                                    conn.connect()
                                    action=tdata.Action(tdata.ActionType.destroy)
                                    mess = action.get_message()
                                    conn.send(mess)
                                    conn.disconnect()
                                    logger.info("Task on address {0}:{1} was destroyed".format(host, str(port)))
                                except:
                                    pass
                    os.remove(file) 
        time.sleep(1)
        if self.output is not None:
            # try kill next communicator
            self.output.kill_next()
        logger.info("Comunicator start destroying process")
        
    def _destroy(self):
        """Terminate this application - last possibilities"""
        logger.error("Communicator was destroyed")
        sys.exit(6)
