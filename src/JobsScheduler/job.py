import sys
sys.path.insert(1, './twoparty/pexpect')
if sys.version_info[0] != 3 or sys.version_info[1] < 4:
    sys.path.insert(2, './twoparty/enum')

import os
import json
import logging
import subprocess
import time
from communication.installation import Installation
import data.communicator_conf as comconf
import communication.installation as inst
from communication import Communicator
import data.transport_data as tdata

from communication.installation import __ins_files__

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
    try:
        import fdpexpect
        import pexpect
        
        fd = fdpexpect.fdspawn(err)
        txt = fd.read_nonblocking(size=10000, timeout=5)
        txt = str(txt, 'utf-8').strip()
    except pexpect.TIMEOUT:
        return None
    except Exception as err:
        logger.warning("Task output error:" + str(err))
        return None
    return txt

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
    directory, comconf.CommType.job.value)
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
logger.info("Start")
# test if config was read
logger.info('Configuration file: %s', job_configuration['configuration_file'])
Installation.prepare_popen_env_static(com_conf.python_env, com_conf.libs_env)
process = subprocess.Popen([com_conf.python_env.python_exec,"test_task.py",
    Installation.get_result_dir_static(com_conf.mj_name)], stderr=subprocess.PIPE)
return_code = process.poll()
if return_code is not None:
    logger.info("read_line")
    out =  read_err(process.stderr)
    logger.error("Can not start test task (return code: " + str(return_code) +
        ",stderr:" + out + ")")
    sys.exit("Can not start test task")

directory = os.path.sep + os.path.join(*directory.split('/')[:-1])

# run flow123d
import pexpect
term = pexpect.spawn('bash')
for line in com_conf.cli_params:
    term.sendline(line)
    term.expect('.*' + line + '\r\n')
    time.sleep(1)
    term.expect(".*\$ ")
    logger.debug('CLI PARAMS> ' + str(term.before, 'utf-8') + '\n' + str(term.after, 'utf-8').strip())
flow_execute = com_conf.flow_path + \
               ' -s ' + os.path.join(directory, job_configuration['configuration_file']) + \
               ' -o ' + os.path.join(directory, 'res', mj_id)
logger.debug('Flow command: ' + flow_execute)
term.sendline(flow_execute)
term.expect('.*' + flow_execute + '\r\n')
time.sleep(1)
term.expect(".*\$ ")
logger.debug('FLOW OUTPUT> ' + str(term.before, 'utf-8') + '\n' + str(term.after, 'utf-8').strip())
term.sendline('exit')

out = read_err(process.stderr)
if out is not None and len(out)>0 and not out.isspace():
    logger.warning("Message in stderr:" + out)
    
if __name__ != "job":
    # no doc generation
    comunicator.run()
   
comunicator.close()   
    
logger.info( "End" ) 


