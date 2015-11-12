"""mj_service test file"""

import sys
import time
import logging

sys.path.insert(1, './twoparty/pexpect')
if sys.version_info[0] != 3 or sys.version_info[1] < 4:
    sys.path.insert(2, './twoparty/enum')

from data.states import MJState, JobsState, JobState, TaskStatus
from communication import JobsCommunicator
import data.communicator_conf as comconf
import communication.installation as inst
import data.transport_data as tdata

logger = logging.getLogger("Remote")

def  mj_action_function_before(message):
    """before action function"""
    global mj_name, start_time
    if message.action_type == tdata.ActionType.get_state:
        state = MJState(mj_name)
        state.insert_time = start_time +10
        state.qued_time = start_time +20
        state.start_time = start_time
        state.run_interval=50
        state.status=TaskStatus.running
        state.known_jobs = 2
        state.estimated_jobs = 2
        state.finished_jobs = 0
        state.running_jobs = 2
        action = tdata.Action(tdata.ActionType.state)
        action.data.set_data(state)
        return False, action.get_message()        
    return comunicator.standart_action_function_before(message)
    
def  mj_action_function_after(message,  response):
    """before action function"""
    global mj_name, start_time
    if message.action_type == tdata.ActionType.download_res:
        states = JobsState()
        state = JobState('test1')
        state.insert_time = start_time +10
        state.qued_time = start_time +20
        state.start_time = start_time
        state.run_interval=50
        state.status=TaskStatus.running
        states.jobs.append(state)
        state2 = JobState('test2')
        state2.insert_time = start_time +15
        state2.qued_time = start_time +25
        state2.start_time = start_time + 5
        state2.run_interval=45
        state2.status=TaskStatus.running
        states.jobs.append(state2)
        states.save_file(inst.Installation.get_result_dir_static(mj_name))
    return comunicator.standart_action_function_after(message,  response)

i = 0
def  mj_idle_function():
    """This function will be call, if meesage is not receive in run function."""
    global i
    i += 1
    if i == 1:
        comunicator.add_job("test1", None)
    if i == 2:
        comunicator.add_job("test2", None)


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

comunicator = JobsCommunicator(com_conf, mj_id, mj_action_function_before,
                               mj_action_function_after, mj_idle_function)
if __name__ != "mj_service":
    # no doc generation
    comunicator.run()
comunicator.close()

