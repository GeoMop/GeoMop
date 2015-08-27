"""multijob test file"""

import sys
import subprocess
import data.transport_data as tdata
sys.path.insert(1, './twoparty/pexpect')

import logging
import data.communicator_conf as comconf
from communication.communicator import Communicator
import data.installation as dinstall

def  mj_action_funcion(message):
    """action function"""
    if message.action_type == tdata.ActionType.installation:
        logging.debug("Job apllication began start")
        try:
            installation = dinstall.Installation()
            installation.local_copy_path()           
            subprocess.Popen(installation.get_args("job"))
            action = tdata.Action(tdata.ActionType.ok)
        except(OSError, ValueError) as err:
            logging.error("Start of job apllication raise error: " + str(err))
            action=tdata.Action(tdata.ActionType.error)
            action.action.data["msg"] = "Next communicator can not be run"        
        return False, True, action.get_message()
    return False, True, None

ccom = comconf.CommunicatorConfig()
ccom.communicator_name = "multijob"
ccom.log_level = logging.DEBUG
ccom.input_type = comconf.InputCommType.socket
comunicator = Communicator(ccom, mj_action_funcion)
comunicator.run()
comunicator.close()

