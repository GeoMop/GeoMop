import sys
import logging
sys.path.insert(1, './twoparty/pexpect')

import data.communicator_conf as comconf
from communication.communicator import Communicator
import data.transport_data as tdata

ccom = comconf.CommunicatorConfig()
ccom.output_type = comconf.OutputCommType.ssh
ccom.communicator_name = "app"
ccom.next_communicator = "delegator"
ccom.uid = "test"
ccom.pwd = "MojeHeslo123"
ccom.log_level = logging.DEBUG

comunicator = Communicator(ccom)
comunicator.install()
comunicator.exec_()

action = tdata.Action(tdata.ActionType.installation)
message = action.get_message()
comunicator.send_message(message)
mess = comunicator.receive_message()

action = tdata.Action(tdata.ActionType.stop)
message = action.get_message()
comunicator.send_message(message)
mess = comunicator.receive_message()

comunicator.close()
