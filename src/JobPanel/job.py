import sys
import os



import json
import logging
import subprocess
import time

from .communication import installation as inst
from .communication import Communicator
from .communication.installation import Installation
from .communication.installation import __ins_files__, __input_dir__

import data.communicator_conf as comconf
import data.transport_data as tdata


logger = logging.getLogger("Remote")
finished = False
rc = 0

def  job_action_function_after(message,  response):
        """before action function - all logic is in after function"""
        return response
        
def  job_action_function_before(message):
    """before action function"""
    if message.action_type == tdata.ActionType.get_state:
        global finished,  rc
        if finished:
            action = tdata.Action(tdata.ActionType.job_state)
            action.data.set_data(rc)
            return False, action.get_message() 
        return_code = process.poll()
        if return_code is not None:
            finished = True 
            rc = return_code
            out =  read_err(process.stderr)
            if out is None:
                out = ""
            if len(out)>0 and return_code==0:
                if return_code==0:
                    logger.warning("Flow123d output message: " + out)
            if return_code!=0:
                logger.error("Flow123d error(return code: " + str(return_code) +
                    ",stderr:" + out + ")")
        action = tdata.Action(tdata.ActionType.job_state)
        action.data.set_data(return_code)
        return False, action.get_message()
    if message.action_type == tdata.ActionType.stop:
        logger.info("Stop signal is received")
        if not finished:
            process.terminate()
            logger.info("Job process will be terminated.")
        comunicator.stop =True
        action = tdata.Action(tdata.ActionType.ok)
        return False, action.get_message()
    action=tdata.Action(tdata.ActionType.error)
    action.data.data["msg"] = "Unsupported job communicator message"
    return False, action.get_message()
    
def read_err(err):
    if err is None:
        return None
    try:
        txt = err.read().strip()
    except Exception as err:
        logger.warning("Task output error:" + str(err))
        return None
    return txt

if len(sys.argv)<3:
    raise Exception('Multijob name as application parameter is require')
mj_id = None
mj_name = sys.argv[1]
an_name = sys.argv[2]
if len(sys.argv) > 3 and sys.argv[3] != "&":
    mj_id = sys.argv[3]

# Load from json file
com_conf = comconf.CommunicatorConfig()
if os.path.isdir(mj_name) and  os.path.isabs(mj_name):
    directory = os.path.join(mj_name, inst.__conf_dir__)
else:
    directory = inst.Installation.get_config_dir_static(mj_name, an_name)
path = comconf.CommunicatorConfigService.get_file_path(
    directory, comconf.CommType.job.value)
    
if __name__ == "job":
    # no doc generation
    exit

try:
    with open(path, "r") as json_file:
        comconf.CommunicatorConfigService.load_file(json_file, com_conf)
except Exception as error:
    logger.error(error)
    raise error

# TODO move config loading elsewhere
def load_configuration(filepath):
    """Load job configuration from file."""
    data = {}
    try:
        with open(filepath, 'r') as file:
            data = json.load(file)
    except Exception as exc:
        logger.error(exc)
    return data[mj_id]

job_configuration = load_configuration(
    os.path.join(directory, __ins_files__['job_configurations']))
"""job configurations"""

# Use com_conf instead of ccom
comunicator = Communicator(com_conf, mj_id,  job_action_function_before, job_action_function_after)
logger.debug("Mj config dir {0}({1})".format(path, mj_name))
logger.info("Start")
# test if config was read
directory = os.path.split(directory)[0]
conf_file= job_configuration['configuration_file'].replace('/', os.path.sep)
logger.info('Configuration file: %s', conf_file)
# run flow123d
if len(com_conf.cli_params)>0:
    try:
        logger.debug('Run commands before Flow123d')        
        for line in com_conf.cli_params:
            logger.debug("Run "+line)
            pre_execute = line.split()
            si = None 
            if sys.platform == "win32":
                si = subprocess.STARTUPINFO()
                si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            process = subprocess.Popen(pre_execute, stdout=subprocess.PIPE, 
                stderr=subprocess.STDOUT, shell=True, startupinfo=si)
            return_code = process.wait()
            if return_code is None or return_code!=0:
                out =  read_err(process.stderr)
                if out is None:
                    out = ""
                logger.error("Preparation error (return code: " + str(return_code) +
                    ",stderr:" + out + ")")
                finished = True
    except Exception as err:    
        logger.error('Preparation error ({0})'.format(err))
        time.sleep(1)
if com_conf.flow_path is None:
    com_conf.flow_path = ""
    
flow_execute = [com_conf.flow_path, 
                            '-s', 
                            os.path.join(directory, __input_dir__, conf_file), 
                            '-o', 
                            os.path.join(directory, 'res', mj_id)
                        ]
logger.debug("Run "+" ".join(flow_execute))
Installation.prepare_popen_env_static(com_conf.python_env, com_conf.libs_env)
try:
    si = None 
    if sys.platform == "win32":
        si = subprocess.STARTUPINFO()
        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    process = subprocess.Popen(flow_execute,stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT, startupinfo=si)
    time.sleep(0.1)
    return_code = process.poll()
    if return_code is not None:
        out =  read_err(process.stderr)
        logger.error("Can not start Flow123d (return code: " + str(return_code) +
            ",stderr:" + out + ")")
        finished = True
        rc=-1
    else:
        logger.debug('Flow123d is running')
    out = read_err(process.stderr)
    if out is not None and len(out)>0 and not out.isspace():
        logger.warning("Message in stderr:" + out)
except Exception as err:    
    logger.error('Can not start Flow123d ({0})'.format(err))
    finished = True
    rc=-1

comunicator.run()
   
comunicator.close()   
    
logger.info( "End" ) 


