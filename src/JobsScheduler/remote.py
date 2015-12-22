"""delegator test file"""
import sys
import logging
import threading

sys.path.insert(1, './twoparty/pexpect')
if sys.version_info[0] != 3 or sys.version_info[1] < 4:
    sys.path.insert(2, './twoparty/enum')

import data.transport_data as tdata
import data.communicator_conf as comconf
import communication.installation as inst
from communication import JobsCommunicator
from  communication.pbs_output_comm import PbsOutputComm
from  communication.exec_output_comm import  ExecOutputComm

import signal
def end_handler(signal, frame):
    comunicator.close()
        
signal.signal(signal.SIGINT, end_handler)

started_jobs = {}

class JobStarter():
    """Class for job starting"""
    def __init__(self, conf, id):         
        """job data for communication"""
        self.output = None
        """Job output connection"""
        self.id = id
        """Job id"""
        if conf.output_type == comconf.OutputCommType.pbs:
            old_name = conf.pbs.name
            conf.pbs.name = id
            self.output = PbsOutputComm(conf.mj_name, conf.port, conf.pbs)
            conf.pbs.name = old_name
            self.output.set_env_params(conf.python_env,  conf.libs_env)
        elif conf.output_type == comconf.OutputCommType.exec_:
            self.output = ExecOutputComm(conf.mj_name, conf.port)
            self.output.set_env_params(conf.python_env,  conf.libs_env)
        self.output.installation.local_copy_path()
        """Start job"""
        t = threading.Thread(target= self.output.exec_,
            args=( conf.next_communicator,conf.mj_name, self.id ))
        t.daemon = True
        t.start() 
        
    def get_connection(self):
        """return port and host"""
        if self.output.initialized:
            return self.output.host, self.output.port
        else:
            return None, None
 
def  remote_action_function_before(message):
    """before action function"""
    global mj_name, start_time
    if message.action_type == tdata.ActionType.download_res:
        # processing in after function
        if not comunicator.conf.direct_communication:
            return False, None
    if message.action_type == tdata.ActionType.get_state:
        state = comunicator.get_state()
        action = tdata.Action(tdata.ActionType.state)
        action.data.set_data(state)
        return False, action.get_message()  
    if message.action_type == tdata.ActionType.installation:            
        resent, mess = super(JobsCommunicator, comunicator).standart_action_function_before(message)
        if comunicator.is_installed():
            action = tdata.Action(tdata.ActionType.ok)
            return False, action.get_message()                        
        return resent, mess
    if message.action_type == tdata.ActionType.set_start_jobs_count:
        comunicator.set_start_jobs_count(
            message.get_action().data.data["known_jobs"], 
            message.get_action().data.data["estimated_jobs"])
        action = tdata.Action(tdata.ActionType.ok)
        return False, action.get_message()
    if message.action_type == tdata.ActionType.add_job:        
        if comunicator.conf.direct_communication:
            if comunicator.conf.output_type == comconf.OutputCommType.none or \
                comunicator.conf.output_type == comconf.OutputCommType.ssh:
                action=tdata.Action(tdata.ActionType.error)
                action.data.data["msg"] = "Communacion to job must be over socket"
            else:
                id = message.get_action().data.data['id']
                if id in started_jobs:
                    host, port = started_jobs[id].get_connection()
                    if host is None:
                        action=tdata.Action(tdata.ActionType.action_in_process)
                    else:
                        # ToDo for remote exec return host (not localhost-])
                        action=tdata.Action(tdata.ActionType.job_conn)
                        action.data.set_conn(host, port)
                else:
                    started_jobs[id] = JobStarter(comunicator.conf, id)
                    action=tdata.Action(tdata.ActionType.action_in_process) 
                mess = action.get_message() 
            return False, mess 
        else:
            id = message.get_action().data.data['id']
            comunicator.add_job(id)
            action = tdata.Action(tdata.ActionType.ok)
            return False, action.get_message()
    return super(JobsCommunicator, comunicator).standart_action_function_before(message)
    
def  remote_action_function_after( message,  response):
    """after action function"""
    global mj_name
    if message.action_type == tdata.ActionType.download_res:
        if not comunicator.conf.direct_communication:
            states =  comunicator.get_jobs_states()
            states.save_file(inst.Installation.get_result_dir_static(mj_name))
            action = tdata.Action(tdata.ActionType.ok)
            return action.get_message()
    return super(JobsCommunicator, comunicator).standart_action_function_after( message,  response)
    
logger = logging.getLogger("Remote")

if len(sys.argv)<2:
    raise Exception('Multijob name as application parameter is require')
mj_id = None
mj_name = sys.argv[1]
if len(sys.argv) > 2 and sys.argv[2] != "&":
    mj_id = sys.argv[2]

# Load from json file
com_conf = comconf.CommunicatorConfig(mj_name)
directory = inst.Installation.get_config_dir_static(mj_name)
path = comconf.CommunicatorConfigService.get_file_path(
    directory, comconf.CommType.remote.value)
try:
    with open(path, "r") as json_file:
        comconf.CommunicatorConfigService.load_file(json_file, com_conf)
except Exception as error:
    logger.error(error)
    raise error

comunicator = JobsCommunicator(com_conf, mj_id, remote_action_function_before, remote_action_function_after)

if __name__ != "remote":
    # no doc generation
    try:
        comunicator.run()
    except Exception as err:
        comunicator.close()
        logger.info("Application stop for uncatch error:" + str(err)) 
        sys.exit(1)    
comunicator.close()
