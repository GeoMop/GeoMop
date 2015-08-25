"""multijob test file"""

import sys
import subprocess
import data.transport_data as tdata
sys.path.insert(1, './twoparty/pexpect')

import logging
import data.communicator_conf as comconf
from communication.communicator import Communicator

def  mj_action_funcion(message):
    """action function"""
    if message.action_type == tdata.ActionType.installation:
        subprocess.Popen(comunicator.output.installation.get_asgs("job"))
        action = tdata.Action(tdata.ActionType.ok)
        return False, True, action.get_message()
    return False, True, None

ccom = comconf.CommunicatorConfig()
ccom.communicator_name = "multijob"
ccom.log_level = logging.DEBUG
ccom.input_type = comconf.InputCommType.socket
comunicator = Communicator(ccom, mj_action_funcion)
comunicator.run()
comunicator.close()

