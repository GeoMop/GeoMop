"""Test application"""
import sys
import logging
import time
sys.path.insert(1, './twoparty/pexpect')

import data.communicator_conf as comconf
from communication import Communicator
import data.transport_data as tdata

if len(sys.argv)<2:
    raise Exception('Multijob name as application parameter is require')
mj_id = None
mj_name = sys.argv[1]
if len(sys.argv)>2 and sys.argv[2] != "&":
    mj_id = sys.argv[2]

ccom = comconf.CommunicatorConfig(mj_name)
ccom.output_type = comconf.OutputCommType.ssh
ccom.communicator_name = "app"
ccom.next_communicator = "delegator"
ccom.ssh=comconf.SshConfig()
ccom.ssh.uid = "test"
ccom.ssh.pwd = "MojeHeslo123"
ccom.ssh.host = "localhost"

# ccom.ssh.uid = "pavel.richter"
# ccom.ssh.pwd = "p256v22l"
# ccom.ssh.host = "hydra.kai.tul.cz"
# ccom.scl_enable_exec = "python33"
ccom.log_level = logging.DEBUG

comunicator = Communicator(ccom, mj_id)
comunicator.install()

comunicator.send_long_action(tdata.Action(tdata.ActionType.installation))
time.sleep(120)

comunicator.send_long_action(tdata.Action(tdata.ActionType.download_res))
comunicator.download()

mess = comunicator.send_long_action(tdata.Action(tdata.ActionType.stop))
comunicator.close()
