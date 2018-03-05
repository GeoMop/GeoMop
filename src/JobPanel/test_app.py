"""Test application"""
import sys
import logging
import time
sys.path.insert(1, './twoparty/pexpect')

import JobPanel.data.communicator_conf as comconf
from JobPanel.communication import Communicator
import JobPanel.data.transport_data as tdata
import JobPanel.communication.installation as inst
from JobPanel.data.states import  JobsState, TaskStatus

logger = logging.getLogger("Remote")

if len(sys.argv)<2:
    raise Exception('Multijob name as application parameter is require')
mj_id = None
mj_name = sys.argv[1]
if len(sys.argv)>2 and sys.argv[2] != "":
    mj_id = sys.argv[2]

# Load from json file
com_conf = comconf.CommunicatorConfig(mj_name)
directory = inst.Installation.get_config_dir_static(mj_name, "geomop_installation")
path = comconf.CommunicatorConfigService.get_file_path(
    directory, comconf.CommType.app.value)
try:
    with open(path, "r") as json_file:
        comconf.CommunicatorConfigService.load_file(json_file, com_conf)
except Exception as error:
    logger.error(error)
    raise error

comunicator = Communicator(com_conf, mj_id)
comunicator.lock_installation(com_conf)
comunicator.install()
comunicator.unlock_installation(mj_name)

old_phase = TaskStatus.installation
sec = time.time() + 600
message = tdata.Action(tdata.ActionType.installation).get_message()
mess = None
while sec > time.time():
    comunicator.send_message(message)
    mess = comunicator.receive_message(120)
    if mess is None:
        break
    if mess.action_type == tdata.ActionType.install_in_process:
        phase = mess.get_action().data.data['phase']
        if phase is not old_phase:
            # add to queue
            pass
        pass
    else:
        break
    time.sleep(10)

time.sleep(30)

comunicator.send_long_action(tdata.Action(tdata.ActionType.download_res))
comunicator.download()
states = JobsState()
states.load_file(inst.Installation.get_result_dir_static(mj_name))
time.sleep(30)

mess = comunicator.send_long_action(tdata.Action(tdata.ActionType.get_state))
data = mess.get_action().data
if mess.action_type == tdata.ActionType.state:
    state=data.get_mjstate(mj_name)

comunicator.send_long_action(tdata.Action(tdata.ActionType.interupt_connection))
comunicator.interupt()
time.sleep(30)

comunicator.restore()
comunicator.send_long_action(tdata.Action(tdata.ActionType.restore_connection))
time.sleep(60)

comunicator.send_long_action(tdata.Action(tdata.ActionType.download_res))
comunicator.download()

mess = comunicator.send_long_action(tdata.Action(tdata.ActionType.stop))
comunicator.close()
comunicator.unlock_application(mj_name)
