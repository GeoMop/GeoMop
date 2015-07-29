import sys
import data.transport_data as tdata
sys.path.insert(1, './twoparty/pexpect')

import data.communicator_conf as comconf
from communication.comunicator import Communicator

ccom = comconf.CommunicatorConfig()
ccom.input_type = comconf.InputCommType.std
comunicator = Communicator(ccom)
comunicator.run()
comunicator.close()

def  standart_action_funcion(message):
    if message.action_type == tdata.ActionType.installation:
        action = tdata.Action(tdata.ActionType.ok)
        return False, True, action.get_message()
    return False, True, None
