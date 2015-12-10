"""mj_service test file"""

import sys
import time
import logging

sys.path.insert(1, './twoparty/pexpect')
if sys.version_info[0] != 3 or sys.version_info[1] < 4:
    sys.path.insert(2, './twoparty/enum')

from communication import JobsCommunicator
import data.communicator_conf as comconf
import communication.installation as inst
import data.transport_data as tdata

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

i = 0
def  mj_idle_function():
    """This function will be call, if meesage is not receive in run function."""
    global i
    i += 1
    if i == 1:
        comunicator.add_job("test1")
    if i == 2:
        comunicator.add_job("test2")


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
comunicator.set_start_jobs_count(2, 0)
if __name__ != "mj_service":
    # no doc generation
    comunicator.run()
comunicator.close()
logger.info("Application " + comunicator.communicator_name + " is stopped")
