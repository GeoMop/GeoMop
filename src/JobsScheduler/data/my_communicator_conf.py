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

    def __init__(self, name=None, with_socket=False, walltime="", nodes="1",
                 ppn="1", mem="400mb", scratch="400mb"):
        """init"""
        self.name = name
        """name as unique job identifier for files"""
        self.with_socket = with_socket  # multijob true; job false
        """Initialize communication over socket"""
        self.walltime = walltime
        self.nodes = nodes
        self.ppn = ppn
        self.mem = mem
        self.scratch = scratch


class SshConfig(object):
    """
    Class for ssh configuration
    """

    def __init__(self, name=None, host="localhost", port="22", uid="", pwd=""):
        """init"""
        self.name = name
        self.host = host
        self.port = port
        self.uid = uid
        self.pwd = pwd

    def __str__(self):
        return json.dumps(self.__dict__)


class CommunicatorConfig(object):
    """
    CommunicatorConfiguration contains data for initialization
    :class:`communication.communicator.Communicator` class. This data is
    serialized by gui application and save as file for later loading by
    :class:`communication.communicator.Communicator`.
    """

    def __init__(self):
        self.mj_name = "mj"
        """folder name for multijob data"""

        self.input_type = InputCommType.none
        """Input communication type"""

        self.output_type = OutputCommType.none
        """Output communication type"""

        self.communicator_name = ""
        """this communicator name for login file, ..."""

        self.next_communicator = ""
        """communicator file that will be start"""

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

        self.scl_enable_exec = None
        """Enable python exec set name over scl"""

        self.ssh = SshConfig()

        self.pbs = PbsConfig()
        """Pbs settings class :class:`data.communicator_conf.PbsConfig`"""

    def save_to_json_file(self, json_file):
        data = dict(self.__dict__)
        data["ssh"] = self.ssh.__dict__
        data["pbs"] = self.pbs.__dict__
        json.dump(data, json_file, indent=4, sort_keys=True)
        logging.info("%s:%s saved to JSON.", self.communicator_name,
                     self.mj_name)

    def load_from_json_file(self, json_file):
        data = json.load(json_file)
        data["ssh"] = SshConfig(**data["ssh"])
        data["pbs"] = PbsConfig(**data["pbs"])
        self.__dict__ = data
        logging.info("%s:%s loaded from JSON.", self.communicator_name,
                     self.mj_name)
