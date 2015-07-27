import sys
sys.path.insert(1, './twoparty/pexpect')

import data.communicator_conf as comconf
from communication.comunicator import Communicator

ccom = comconf.CommunicatorConfig()
ccom.output_type = comconf.OutputCommType.ssh
ccom.next_communicator = "delegator"
ccom.uid = "test"
ccom.pwd = "MojeHeslo123"
ccom.install_path = "jobs"

comunicator = Communicator(ccom)
