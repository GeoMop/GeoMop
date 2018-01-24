from .service_base import ServiceBase
from . import config_builder
from .json_data import JsonDataNoConstruct

import threading
import time


class ServiceFrontend(ServiceBase):
    """
    Service that running in GUI process and provide communication with backend.
    Allows starting, stopping jobs and acquiring their statuses.


    Usage:

        - set application data to constructor
        - add job id (key) to array (start_jobs,stop_jobs,resume_jobs,terminate_jobs)
        - if current job is changed, set it
        - each 0.5s call check function in main thread, after check returning should be done:

                - from arrays state_change_jobs,results_change_jobs,jobs_change_jobs pull
                   jobs, and fix graphic presentation
                - if application is stopping, check run_jobs and start_jobs arrays (in this case,
                  check function can be call with higher frequency)

        - call stop_all or pause_all function and wait till run_jobs, delete_jobs and start_jobs array is not empty


     JB, TODO: Describe better data structures. What are individual states/queues exactly?
    """

    def __init__(self, data_app):
        self.mj_map = JsonDataNoConstruct()
        """map of mj_id -> [child_id]"""

        # ToDo: nezadavat natvrdo
        env = {"__class__": "Environment",
               "geomop_root": "/home/radek/work/GeoMop/src",
               "geomop_analysis_workspace": "/home/radek/work/workspace",
               "python": "python3"}

        cl = {"__class__": "ConnectionLocal",
              "address": "localhost",
              "environment": env,
              "name": "local"}
        super().__init__({"service_host_connection": cl,
                          "mj_map": {}})

        # Interface old
        ###############
        #self._interface_lock = threading.Lock()
        """Lock for interface"""
        self._current_job = None
        """
        current job id
        What is current_job?
        """
        self._start_jobs = []
        """array of job ids, that will be started"""
        self._resume_jobs = []
        """array of jobs ids, that will be resume"""
        self._stop_jobs = []
        """array of jobs ids, that will be stopped"""
        self._delete_jobs = []
        """array of jobs ids, that will be stopped"""
        self._run_jobs = []
        """array of running jobs ids"""
        self._terminate_jobs = []
        """array of jobs ids, that will be destroyed (try restart job and delete all processes and data)"""
        self._state_change_jobs = []
        """array of jobs ids, that have changed state"""
        self._results_change_jobs = []
        """array of jobs ids, that have changed results"""
        self._jobs_change_jobs = []
        """array of jobs ids, that have changed jobs state"""
        self._jobs_deleted = {}
        """
        Dictionary of jobs ids=>None (ids=>error), that was deleted data.
        If job was not deleted, in dictionary value is error text
        """
        self._logs_change_jobs=[]
        """array of jobs ids, that have changed jobs logs"""


        self._data_app = data_app
        self._backend_proxy = None

    # Interface old
    ###############
    def poll(self):
        """
        This function plans and makes all the needed actions in the main thread.
        Function should be called periodically from the UI.
        """
        pass

    def pause_all(self):
        """Pause all running and starting jobs (use when app is closing)."""
        pass

    def stop_all(self):
        """stop all running and starting jobs"""
        pass



    def start_backend(self):
        # environment
        # ToDo: nezadavat natvrdo
        env = {"__class__": "Environment",
               "geomop_root": "/home/radek/work/GeoMop/src",
               "geomop_analysis_workspace": "/home/radek/work/workspace",
               "python": "python3"}

        # service data
        cd = {"__class__": "ConnectionLocal",
              # ToDo: nezadavat natvrdo
              "address": "172.17.42.1",
              "environment": env,
              "name": "docker"}
        pd = {"__class__": "ProcessDocker",
              "executable": {"__class__": "Executable",
                             "path": "JobPanel/services/backend_service.py",
                             "script": True}}
        service_data = {"service_host_connection": cd,
                        "process": pd,
                        "workspace": "",
                        "config_file_name": "backend_service.conf"}

        # start backend
        child_id = self.request_start_child(service_data)
        self._backend_proxy = self._child_services[child_id]

    def stop_backend(self):
        answer = []
        self._backend_proxy.call("request_stop", None, answer)
        #time.sleep(5)

    # Interface new
    ###############
    def mj_start(self, mj_id):
        """Start multijob"""
        if mj_id in self.mj_map:
            return
        self.mj_map[mj_id] = None

        mj_conf = config_builder.build(self._data_app, mj_id)
        answer = []
        self._backend_proxy.call("request_start_child", mj_conf, answer)
        self.mj_map[mj_id] = answer

    def mj_stop(self, mj_id):
        """Stop multijob"""
        if mj_id in self.mj_map:
            child_id_list = self.mj_map[mj_id]
            if len(child_id_list) > 0:
                answer = []
                self._backend_proxy.call("request_stop_child", child_id_list[0], answer)
            # ToDo: co kdyz existuje, ale jeste nemame child_id?

    def mj_delete(self, mj_id):
        """Delete multijob"""
        if mj_id in self.mj_map:
            del self.mj_map[mj_id]


