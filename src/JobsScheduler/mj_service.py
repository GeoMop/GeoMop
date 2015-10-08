"""mj_service test file"""

import sys
sys.path.insert(1, './twoparty/pexpect')
if sys.version_info[0] != 3 or sys.version_info[1] < 4:
    sys.path.insert(2, './twoparty/enum')
    
import subprocess
import data.transport_data as tdata

import logging
import data.communicator_conf as comconf
from communication import Communicator
from communication import Installation

def  mj_action_funcion_before(message):
    """before action function"""
    if message.action_type == tdata.ActionType.installation:
        logging.debug("Job apllication began start")
        try:
            installation = Installation(ccom.mj_name)
            # installation.set_install_params("/opt/python/bin/python3.3", None)
            installation.local_copy_path()           
            subprocess.Popen(installation.get_args("job"))
            action = tdata.Action(tdata.ActionType.ok)
        except(OSError, ValueError) as err:
            logging.error("Start of job apllication raise error: " + str(err))
            action=tdata.Action(tdata.ActionType.error)
            action.data.data["msg"] = "Next communicator can not be run"        
        return False, True, action.get_message()
    if message.action_type == tdata.ActionType.stop:
        # processing in after function
        return False, False, None
    return comunicator.standart_action_funcion_before(message)
    
def  mj_action_funcion_after(message,  response):
    """before action function"""
    if message.action_type == tdata.ActionType.stop:
        # ToDo:: close all jobs 
        comunicator.stop = True
        logging.info("Stop signal is received")
        action = tdata.Action(tdata.ActionType.ok)
        return action.get_message()
    return comunicator.standart_action_funcion_after(message,  response)

ccom = comconf.CommunicatorConfig()
ccom.communicator_name = "mj_service"
ccom.log_level = logging.DEBUG
#ccom.input_type = comconf.InputCommType.pbs
ccom.input_type = comconf.InputCommType.socket
comunicator = Communicator(ccom, None, mj_action_funcion_before, mj_action_funcion_after)
if __name__ != "mj_service":
    # no doc generation
    comunicator.run()
comunicator.close()

