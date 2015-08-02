import sys
import data.transport_data as tdata
sys.path.insert(1, './twoparty/pexpect')

import logging
import data.communicator_conf as comconf
from communication.communicator import Communicator

def  standart_action_funcion(message):
    if message.action_type == tdata.ActionType.installation:
        action = tdata.Action(tdata.ActionType.ok)
        return False, True, action.get_message()
    return False, True, None

ccom = comconf.CommunicatorConfig()
ccom.communicator_name = "delegator"
ccom.log_level = logging.DEBUG
ccom.input_type = comconf.InputCommType.std
comunicator = Communicator(ccom, standart_action_funcion)
comunicator.run()
comunicator.close()


