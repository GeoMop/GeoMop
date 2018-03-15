from .service_base import ServiceBase, ServiceStatus
from . import config_builder
from .json_data import JsonData, JsonDataNoConstruct
from services.backend_service import MJReport
from services.multi_job_service import MJStatus
from ui.data.mj_data import MultiJobState
from data.states import TaskStatus as GuiTaskStatus

import threading
import time
import logging


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
        # ToDo: nezadavat natvrdo
        env = {"__class__": "Environment",
               "geomop_root": "/home/radek/work/GeoMop/src",
               "geomop_analysis_workspace": "/home/radek/work/workspace",
               "python": "python3"}

        cl = {"__class__": "ConnectionLocal",
              "address": "localhost",
              "environment": env,
              "name": "local"}
        super().__init__({"service_host_connection": cl})

        self._mj_report = {}
        """MJ report information"""
        self._results_get_mj_report = []
        """Result list of get mj report request"""
        self._mj_report_time = 0.0
        """Last time request_get_mj_report sent"""


        # Interface old
        ###############
        self._start_jobs = []
        """array of job ids, that will be started"""
        self._delete_jobs = []
        """array of jobs ids, that will be stopped"""
        self._run_jobs = []
        """array of running jobs ids"""
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

        self._mj_changed_state = set()
        """Set of MJ which changed state, from last call get_mj_changed_state."""

    def _do_work(self):
        self._retrieve_mj_report()

    def _retrieve_mj_report(self):
        """
        Retrieves MJ report data.
        :return:
        """
        # result
        l = len(self._results_get_mj_report)
        for i in range(l-1):
            self._results_get_mj_report.pop(0)
        res = self._results_get_mj_report.pop(0)
        if "error" in res:
            logging.error("Error in retrieving MJ report data")
        else:
            new_mj_report = JsonData.construct_dict(MJReport(), res["data"])
            self._update_mj_report(new_mj_report)

        # send request
        if (self._backend_proxy is not None) and self._backend_proxy._online and (time.time() > self._mj_report_time + 1):
            self._backend_proxy.call("request_get_mj_report", None, self._results_get_mj_report)
            self._mj_report_time = time.time()

    def _update_mj_report(self, new_mj_report):
        """
        Updates MJ report with new information.
        :param new_mj_report:
        :return:
        """
        for k, v in new_mj_report.items():
            # We need update run_interval therefore (v.service_status == ServiceStatus.running)
            if (k not in self._mj_report) or (self._mj_report[k] != v) or (v.service_status == ServiceStatus.running):
                self._mj_report[k] = v

                # update MJ data
                status = GuiTaskStatus.none
                if v.service_status == ServiceStatus.queued:
                    status = GuiTaskStatus.queued
                elif v.service_status == ServiceStatus.running:
                    status = GuiTaskStatus.running
                elif v.service_status == ServiceStatus.done:
                    if v.mj_status == MJStatus.success:
                        status = GuiTaskStatus.finished
                    elif v.mj_status == MJStatus.error:
                        status = GuiTaskStatus.error
                    else:
                        status = GuiTaskStatus.running

                run_interval = 0.0
                if v.done_time:
                    run_interval = v.done_time - v.start_time
                elif v.start_time:
                    run_interval = time.time() - v.start_time

                state = MultiJobState("",
                    status=status,
                    queued_time=v.queued_time,
                    start_time=v.start_time,
                    run_interval=run_interval,
                    known_jobs=v.known_jobs,
                    estimated_jobs=v.estimated_jobs,
                    finished_jobs=v.finished_jobs,
                    running_jobs=v.running_jobs)
                mj = self._data_app.multijobs[k]
                mj.state.update(state)

                self._mj_changed_state.add(k)

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
        # if mj_id in self.mj_map:
        #     return
        # self.mj_map[mj_id] = None

        mj_conf = config_builder.build(self._data_app, mj_id)
        answer = []
        self._backend_proxy.call("request_start_mj", {"mj_id": mj_id, "mj_conf": mj_conf}, answer)
        #self.mj_map[mj_id] = answer

    def mj_stop(self, mj_id):
        """Stop multijob"""
        return
        if mj_id in self.mj_map:
            child_id_list = self.mj_map[mj_id]
            if len(child_id_list) > 0:
                answer = []
                self._backend_proxy.call("request_stop_child", child_id_list[0], answer)
            # ToDo: co kdyz existuje, ale jeste nemame child_id?

    def mj_delete(self, mj_id):
        """Delete multijob"""
        return
        if mj_id in self.mj_map:
            del self.mj_map[mj_id]

    def get_mj_changed_state(self):
        """
        Returns list of MJ which changed state, from last call this method.
        :return:
        """
        ret = list(self._mj_changed_state)
        self._mj_changed_state.clear()
        return ret
