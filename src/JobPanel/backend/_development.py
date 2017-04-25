"""
Data structures:

Environment:
    Installation -
    Workspace - root data dir of GeoMop on remote
    PBS dialects - list of available dialects and their conf data (possible more PBS on one system]
    python
    mpiexec

SSH:
    IP or address - where to execute
    Connection - (socket, SSH) - can be filled automatically on GUI orm IP
    uid
    password

Resource (MJ):
    ExecMethod - ( Docker | Exec | PBS)
    max parallel jobs
    max local processes (same node as MJ)
    Future: TimeLimit, MemoryLimit, generalize form PBS config

    PBS (see data.communicator_conf.PbsConfig):
        dialect
        n_proc
        ppn
        queue
        walltime
        mem
        scratch
        infiniband
        PBS options
        (further options should be dialect specific, GUI should report which option is finally used)
        ...

Analysis (data):
    name,
    reuse_data_from_mj,
    subdir with data,
    Selection of files (actions) to download
    ...

MJ:
    run_no
    Resource
    Analysis

MJProxy:
    MJ status
    Analysis status
    workspace files, status of file: locked (not finished), remote open, remote closed, downloaded - up to date

Paths:
    .... names of standard subdirectories



GUI requests:

handled by backend:
    - start MJ( MJ data ) ... use Popen on remote
    (- start with reuse)
    - list all files of MJ and their dates ... complex dir traversal on remote and return data
    - download particular files from MJ ... through sftp or others from backend
    - kill MJ ... complex process on remote, need to check that process is really killed
    - clean MJ ... dir traversal, killing jobs, ...

handled by MJ:
    - get Analysis status (runtime, estimate, states of actions, ...)
    - get MJ status ( should be connected with Analysis status)
    - get status of Jobs (part of previous)

    - get file list for MJ, for particular Job
      ( we should download even uncomplete results to overlap it with calculation)
    - future: get detailed state data from MJ or Job (e.g. uncomplete VTU files, observe series, ...),
      can get anything stored on filesystem as locally
    - stop MJ



MJ requests:
    - start Job
    - get state of Job
    - get file list of Job
    - stop Job
    - kill Job
    - clean Job

Delegator requests:
    - start service
    - get workspace tree
    - delete paths
    - kill service
"""

import sys
assert sys.version_info >= (3,4)


class JobData:
    pass

class Service(JobData):


    def request_get(self, variable_name):
        return self.__dict__[variable_name]



class DelegatorService:
    pass

class JobService(Service):

    pass

class MultijobService(JobService):
    def start_service(self, service_data):
        pass


class BackendService:
    pass


class ClientService:
    def start_backend(self):
        pass









def start_backend(client_servicerepeater):
    pass




