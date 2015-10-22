"""Configuration of communication unit"""
from enum import Enum, IntEnum
import logging
import json


class OutputCommType(IntEnum):
    """Severity of an error."""
    none = 0
    ssh = 1
    exec_ = 2
    pbs = 3


class InputCommType(IntEnum):
    """Severity of an error."""
    none = 0
    std = 1
    socket = 2
    pbs = 3


class CommType(Enum):
    """Types of communicators"""
    none = ""
    app = "app"
    delegator = "delegator"
    remote = "remote"
    multijob = "multijob"
    job = "job"


class PbsConfig(object):
    """
    Class for configuration qsub command
    """

    def __init__(self, preset=None, with_socket=False):
        """init"""
        if preset:
            self.name = preset[0]
            self.walltime = preset[2]
            self.nodes = preset[3]
            self.ppn = preset[4]
            self.mem = preset[5]
            self.scratch = preset[5]
        else:
            self.name = None
            """name as unique job identifier for files"""
            self.walltime = ""
            self.nodes = "1"
            self.ppn = "1"
            self.mem = "400mb"
            self.scratch = "400mb"
        self.with_socket = with_socket  # multijob true; job false
        """Initialize communication over socket"""


class SshConfig(object):
    """
    Class for ssh configuration
    """

    def __init__(self, preset=None):
        """init"""
        if preset:
            self.name = preset[0]
            self.host = preset[2]
            self.port = preset[3]
            self.uid = preset[4]
            self.pwd = preset[5]
        else:
            self.name = None
            self.host = "localhost"
            self.port = "22"
            self.uid = ""
            self.pwd = ""

    def __str__(self):
        return json.dumps(self)


class CommunicatorConfig(object):
    """
    CommunicatorConfiguration contains data for initialization
    :class:`communication.communicator.Communicator` class. This data is
    serialized by gui application and save as file for later loading by
    :class:`communication.communicator.Communicator`.
    """

    def __init__(self, preset_type=None):
        self.communicator_name = CommType.none.value
        """this communicator name for login file, ..."""

        self.next_communicator = CommType.none.value
        """communicator file that will be start"""

        self.input_type = InputCommType.none
        """Input communication type"""

        self.output_type = OutputCommType.none
        """Output communication type"""

        self.mj_name = "mj"
        """folder name for multijob data"""

        self.port = 5723
        """
        First port for the socket communication with this communicator.
        If this port has the use of another application, socket connection
        is set to next port in order.
        """

        self.log_level = logging.WARNING
        """log level for communicator"""

        self.python_exec = "python3"
        """Python exec command"""

        self.scl_enable_exec = False
        """Enable python exec set name over scl"""

        self.ssh = None
        """Ssh settings class :class:`data.communicator_conf.SshConfig`"""

        self.pbs = None
        """Pbs settings class :class:`data.communicator_conf.PbsConfig`"""

        if preset_type:
            self.preset_type(preset_type)

    def preset_type(self, preset_type):
        # app
        if preset_type == CommType.app.value:
            self.communicator_name = CommType.app.value
            self.next_communicator = CommType.multijob.value
            self.output_type = OutputCommType.exec_

        # delegator
        elif preset_type == CommType.delegator.value:
            self.communicator_name = CommType.delegator.value
            self.next_communicator = CommType.multijob.value
            self.input_type = InputCommType.std
            self.output_type = OutputCommType.exec_
        # mj
        elif preset_type == CommType.multijob.value:
            self.communicator_name = CommType.multijob.value
            self.next_communicator = CommType.job.value
            self.input_type = InputCommType.socket
            self.output_type = OutputCommType.exec_
        # remote
        elif preset_type == CommType.remote.value:
            self.communicator_name = CommType.remote.value
            self.next_communicator = CommType.job.value
            self.input_type = InputCommType.std
            self.output_type = OutputCommType.exec_
        # job
        elif preset_type == CommType.multijob.value:
            self.communicator_name = CommType.job.value
            self.next_communicator = CommType.none.value
            self.input_type = InputCommType.socket
            self.output_type = OutputCommType.none

    def save_to_json_file(self, json_file):
        data = dict(self.__dict__)
        if data["ssh"]:
            data["ssh"] = self.ssh.__dict__
        if data["pbs"]:
            data["pbs"] = self.pbs.__dict__
        json.dump(data, json_file, indent=4, sort_keys=True)
        logging.info("%s:%s saved to JSON.", self.communicator_name,
                     self.mj_name)

    def load_from_json_file(self, json_file):
        data = json.load(json_file)
        if data["ssh"]:
            ssh = SshConfig()
            ssh.__dict__ = data["ssh"]
            data["ssh"] = ssh
        if data["pbs"]:
            pbs = PbsConfig()
            pbs.__dict__ = data["pbs"]
            data["pbs"] = pbs
        self.__dict__ = data
        logging.info("%s:%s loaded from JSON.", self.communicator_name,
                     self.mj_name)
