"""Test application"""
import sys
import logging
import time
sys.path.insert(1, './twoparty/pexpect')

import data.communicator_conf as comconf
from communication import Communicator
import data.transport_data as tdata
import communication.installation as inst

if len(sys.argv)<2:
    raise Exception('Multijob name as application parameter is require')
mj_id = None
mj_name = sys.argv[1]
if len(sys.argv)>2 and sys.argv[2] != "&":
    mj_id = sys.argv[2]

print(mj_name)
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

# Load from json file
com_conf = comconf.CommunicatorConfig(mj_name)
directory = inst.Installation.get_config_dir_static(mj_name)
path = comconf.CommunicatorConfigService.get_file_path(
    directory, comconf.CommType.app.value)
try:
    with open(path, "r") as json_file:
        comconf.CommunicatorConfigService.load_file(json_file, com_conf)
except Exception as error:
    logging.error(error)
    raise error
# Use com_conf instead of ccom


comunicator = Communicator(com_conf, mj_id)
comunicator.install()

comunicator.send_long_action(tdata.Action(tdata.ActionType.installation))
time.sleep(120)

comunicator.send_long_action(tdata.Action(tdata.ActionType.download_res))
comunicator.download()

mess = comunicator.send_long_action(tdata.Action(tdata.ActionType.stop))
comunicator.close()
