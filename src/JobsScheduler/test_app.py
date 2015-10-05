"""Test application"""
import sys
import logging
import time
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

comunicator.send_long_action(tdata.Action(tdata.ActionType.installation))
time.sleep(30)
mess = comunicator.send_long_action(tdata.Action(tdata.ActionType.stop))
comunicator.close()
