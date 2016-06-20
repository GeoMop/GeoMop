"""mj_service test file"""

import sys
import time
import logging
import json
import os

__lib_dir__ = os.path.join(os.path.split(
    os.path.dirname(os.path.realpath(__file__)))[0], "common")
__pexpect_dir__ = os.path.join(os.path.dirname(
    os.path.realpath(__file__)), "twoparty/pexpect")
__enum_dir__ = os.path.join(os.path.dirname(
    os.path.realpath(__file__)), "twoparty/enum")

sys.path.insert(1, __pexpect_dir__)
if sys.version_info[0] != 3 or sys.version_info[1] < 4:
    sys.path.insert(2, __enum_dir__)
if sys.platform == "win32":
    sys.path.insert(2, __lib_dir__)

from communication import JobsCommunicator
import data.communicator_conf as comconf
import communication.installation as inst
import data.transport_data as tdata

from communication.installation import __ins_files__

logger = logging.getLogger("Remote")

def  mj_action_function_before(message):
    """before action function"""
    global mj_name, start_time
    if message.action_type == tdata.ActionType.get_state:
        if com_conf.output_type != comconf.OutputCommType.ssh or \
           com_conf.direct_communication:
            state = comunicator.get_state()
            action = tdata.Action(tdata.ActionType.state)
            action.data.set_data(state)
            return False, action.get_message()        
    return comunicator.standart_action_function_before(message)
    
def  mj_action_function_after(message,  response):
    """before action function"""
    global mj_name
    if message.action_type == tdata.ActionType.download_res:
        if com_conf.output_type != comconf.OutputCommType.ssh or \
           com_conf.direct_communication:
            states =  comunicator.get_jobs_states()
            states.save_file(inst.Installation.get_result_dir_static(mj_name))
    return comunicator.standart_action_function_after(message,  response)


def load_jobs(filepath):
    """Load job configuration from file."""
    data = {}
    try:
        with open(filepath, 'r') as file:
            data = json.load(file)
    except Exception as exc:
        logger.error(exc)
    return data


jobs_to_exec = []
"""names of the jobs to execute"""


def  mj_idle_function():
    """This function will be call, if meesage is not receive in run function."""
    global jobs_to_exec
    if jobs_to_exec:
        job_name = jobs_to_exec.pop()
        comunicator.add_job(job_name)


if len(sys.argv) < 2:
    raise Exception('Multijob name as application parameter is require')
mj_id = None
mj_name = sys.argv[1]
if len(sys.argv) > 2 and sys.argv[2] != "&":
    mj_id = sys.argv[2]

start_time = time.time()
# Load from json file
com_conf = comconf.CommunicatorConfig(mj_name)
directory = inst.Installation.get_config_dir_static(mj_name)
path = comconf.CommunicatorConfigService.get_file_path(
    directory, comconf.CommType.multijob.value)
try:
    with open(path, "r") as json_file:
        comconf.CommunicatorConfigService.load_file(json_file, com_conf)
except Exception as error:
    logger.error(error)
    raise error

jobs = load_jobs(os.path.join(directory, __ins_files__['job_configurations']))
jobs_to_exec = list(jobs.keys())
count = len(jobs)
comunicator = JobsCommunicator(com_conf, mj_id, mj_action_function_before,
                               mj_action_function_after, mj_idle_function)
logger.debug("Set counter to {0} jobs".format(str(count)))
comunicator.set_start_jobs_count(count, 0)

if __name__ != "mj_service":
    # no doc generation
    comunicator.run()
comunicator.close()
logger.info("Application " + comunicator.communicator_name + " is stopped")
