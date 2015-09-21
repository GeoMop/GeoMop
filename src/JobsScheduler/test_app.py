"""Test application"""
import sys
import logging
sys.path.insert(1, './twoparty/pexpect')

import data.communicator_conf as comconf
from communication import Communicator
import data.transport_data as tdata

ccom = comconf.CommunicatorConfig()
ccom.output_type = comconf.OutputCommType.ssh
ccom.communicator_name = "app"
ccom.next_communicator = "delegator"
ccom.uid = "test"
ccom.pwd = "MojeHeslo123"
ccom.host = "localhost"
#ccom.uid = "pavel.richter"
#ccom.pwd = ""
#ccom.host = "hydra.kai.tul.cz"
#ccom.scl_enable_exec = "python33"
ccom.log_level = logging.DEBUG

comunicator = Communicator(ccom)
comunicator.install()

installed = False
while not installed:
    action = tdata.Action(tdata.ActionType.installation)
    message = action.get_message()
    comunicator.send_message(message)
    mess = comunicator.receive_message()
    action = mess.action_type
    if mess.action_type != tdata.ActionType.installation_in_process:
        installed = True
    if __name__ == "test_app":
        break

action = tdata.Action(tdata.ActionType.stop)
message = action.get_message()
comunicator.send_message(message)
mess = comunicator.receive_message()

comunicator.close()
