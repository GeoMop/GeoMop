from .service_base import ServiceBase, ServiceStatus
from . import config_builder
from .json_data import JsonData, JsonDataNoConstruct
from .executor import ProcessDocker
from .path_converter import if_win_win2lin_conv_path
from JobPanel.services.backend_service import MJReport
from JobPanel.services.multi_job_service import MJStatus
from JobPanel.ui.data.mj_data import MultiJobState
from JobPanel.data.states import TaskStatus
from JobPanel.data.secret import Secret
from JobPanel.communication import Installation
from gm_base.global_const import GEOMOP_INTERNAL_DIR_NAME

import threading
import time
import logging
import os
import json
import sys
import random
import psutil


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
        self.backend_process_id = ""
        """Hash of the backend running container"""

        # ToDo: vyresit lepe
        geomop_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
        geomop_analysis_workspace = data_app.workspaces.get_path()
        workspace = ""
        config_file_name = GEOMOP_INTERNAL_DIR_NAME + "/frontend_service.conf"

        # try load frontend service config file
        file = os.path.join(geomop_analysis_workspace,
                            workspace,
                            config_file_name)
        service_data = None
        try:
            with open(file, 'r') as fd:
                try:
                    service_data = json.load(fd)
                except ValueError:
                    pass
        except OSError:
            pass

        if service_data is not None:
            # fix service_data
            if "__class__" in service_data:
                del service_data["__class__"]
            # todo: Asi by se melo znovu nastavit geomop_root a geomop_analysis_workspace pro pripad,
            # ze doslo ke zmene umisteni workspace. To same plati i pro backend.
        else:
            # if file doesn't exist create new config
            env = {"__class__": "Environment",
                   "geomop_root": geomop_root,
                   "geomop_analysis_workspace": geomop_analysis_workspace,
                   "python": "python3"}

            cl = {"__class__": "ConnectionLocal",
                  "address": "localhost",
                  "environment": env,
                  "name": "local"}

            service_data = {"service_host_connection": cl,
                            "workspace": workspace,
                            "config_file_name": config_file_name}

        super().__init__(service_data)

        self._mj_report = {}
        """MJ report information"""
        self._results_get_mj_report = []
        """Result list of get mj report request"""
        self._mj_report_time = 0.0
        """Last time request_get_mj_report sent"""

        self._jobs_deleted = {}
        """
        Dictionary of jobs ids=>None (ids=>error), that was deleted data.
        If job was not deleted, in dictionary value is error text
        """
        self._jobs_downloaded = {}
        """
        Dictionary of jobs ids=>None (ids=>error), that was downloaded data.
        If job was not downloaded, in dictionary value is error text.
        """

        self._data_app = data_app
        self._backend_proxy = None

        self._mj_changed_state = set()
        """Set of MJ which changed state, from last call get_mj_changed_state."""

        self._backend_process_id_saved = False

        self._answers_from_delete = []
        """list of answers from request_delete_mj (mj_id, [answer])"""
        self._answers_from_download = []
        """list of answers from request_download_whole_mj (mj_id, [answer])"""

    def _do_work(self):
        # save backend process id
        if not self._backend_process_id_saved:
            if (self._backend_proxy is not None) and (self._backend_proxy.process_id != ""):
                self.backend_process_id = self._backend_proxy.process_id
                self.save_config()
                self._backend_process_id_saved = True

        self._retrieve_mj_report()
        self._process_delete_answers()
        self._process_download_answers()

    def _retrieve_mj_report(self):
        """
        Retrieves MJ report data.
        :return:
        """
        # result
        l = len(self._results_get_mj_report)
        if l > 0:
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
                status = TaskStatus.none
                if v.proxy_stopped:
                    status = TaskStatus.stopped
                elif v.service_status == ServiceStatus.queued:
                    if v.proxy_stopping:
                        status = TaskStatus.stopping
                    else:
                        status = TaskStatus.queued
                elif v.service_status == ServiceStatus.running:
                    if v.proxy_stopping:
                        status = TaskStatus.stopping
                    else:
                        status = TaskStatus.running
                elif v.service_status == ServiceStatus.done:
                    if v.mj_status == MJStatus.success:
                        status = TaskStatus.finished
                    elif v.mj_status == MJStatus.error:
                        status = TaskStatus.error
                    elif v.mj_status == MJStatus.stopping:
                        status = TaskStatus.stopped
                    else:
                        # todo: divny, nemelo by nikdy nastat
                        status = TaskStatus.running

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

        # remove old items
        for k in [k for k in self._mj_report.keys() if k not in new_mj_report]:
            del self._mj_report[k]

    def _process_delete_answers(self):
        """
        Process answers from request_delete_mj.
        :return:
        """
        done = False
        while not done:
            done = True
            for i in range(len(self._answers_from_delete)):
                if len(self._answers_from_delete[i][1]) > 0:
                    item = self._answers_from_delete.pop(i)
                    res = item[1][0]
                    if "error" in res:
                        logging.error("Error in delete mj")
                    else:
                        self._jobs_deleted[item[0]] = res["data"]
                        if item[0] in self._mj_report:
                            del self._mj_report[item[0]]
                    done = False
                    break

    def _process_download_answers(self):
        """
        Process answers from request_download_whole_mj.
        :return:
        """
        done = False
        while not done:
            done = True
            for i in range(len(self._answers_from_download)):
                if len(self._answers_from_download[i][1]) > 0:
                    item = self._answers_from_download.pop(i)
                    res = item[1][0]
                    if "error" in res:
                        logging.error("Error in download mj")
                    else:
                        self._jobs_downloaded[item[0]] = res["data"]
                    done = False
                    break

    def _get_free_tcp_port(self):
        """
        Returns free tcp port.
        :return:
        """
        while True:
            occupied_ports = [con.laddr.port for con in psutil.net_connections(kind="tcp")]
            port = random.randrange(30001, 60000)
            if port not in occupied_ports:
                return port

    def start_backend(self):
        """
        Starts backend.
        :return:
        """
        workspace = ""
        config_file_name = GEOMOP_INTERNAL_DIR_NAME + "/backend_service.conf"

        # kill old backend container
        self.kill_backend()

        # try load backend service config file
        file = os.path.join(self.get_analysis_workspace(),
                            workspace,
                            config_file_name)
        service_data = None
        try:
            with open(file, 'r') as fd:
                try:
                    service_data = json.load(fd)
                except ValueError:
                    pass
        except OSError:
            pass

        if service_data is not None:
            # fix service_data
            if "__class__" in service_data:
                del service_data["__class__"]
            if "environment" in service_data["process"]:
                del service_data["process"]["environment"]
        else:
            # if file doesn't exist create new config
            env = {"__class__": "Environment",
                   # todo: v budoucnu bude odkazovat primo na instalaci v dockeru
                   "geomop_root": if_win_win2lin_conv_path(self.get_geomop_root()),
                   "geomop_analysis_workspace": if_win_win2lin_conv_path(self.get_analysis_workspace()),
                   "python": "python3"}

            cd = {"__class__": "ConnectionLocal",
                  # ToDo: nezadavat natvrdo, nicmene zpusobi jenom zpozdeni 1 s
                  "address": "172.17.42.1",
                  "environment": env,
                  "name": "docker"}

            pd = {"__class__": "ProcessDocker",
                  "executable": {"__class__": "Executable",
                                 "path": "JobPanel/services/backend_service.py",
                                 "script": True}}

            service_data = {"service_host_connection": cd,
                            "process": pd,
                            "workspace": workspace,
                            "config_file_name": config_file_name}

        # set log level
        service_data["log_all"] = False

        # add secret key
        if "exec_args" not in service_data["process"]:
            service_data["process"]["exec_args"] = {"__class__": "ExecArgs"}
        service_data["process"]["exec_args"]["secret_args"] = [Secret().get_key()]

        # win workaround
        if sys.platform == "win32":
            container_port = 33033
            host_port = self._get_free_tcp_port()
            host_interface = "127.0.0.1"
            service_data["process"]["docker_port_expose"] = [host_interface, host_port, container_port]

            service_data["requested_listen_port"] = container_port

            service_data["listen_address_substitute"] = [host_interface, host_port]

            #service_data["process"]["fterm_path"] = os.path.join(self.get_geomop_root(), "flow123d\\bin\\fterm.bat")

        # start backend
        child_id = self.request_start_child(service_data)
        self._backend_proxy = self._child_services[child_id]

    def stop_backend(self):
        """
        Request stop backend.
        :return:
        """
        answer = []
        self._backend_proxy.call("request_stop", None, answer)
        #time.sleep(5)

    def kill_backend(self):
        """
        Kill backend container.
        :return:
        """
        if self.backend_process_id != "":
            executor = ProcessDocker({"process_id": self.backend_process_id})
            executor.kill()

    def get_backend_status(self):
        """Returns True if backend is online."""
        return (self._backend_proxy is not None) and self._backend_proxy._online

    def mj_start(self, mj_id):
        """Start multijob"""
        err, mj_conf = config_builder.build(self._data_app, mj_id)

        # error handling
        preset = self._data_app.multijobs[mj_id].preset
        mj_config_path = Installation.get_config_dir_static(preset.name, preset.analysis)
        mj_config_path_conf = os.path.join(mj_config_path, GEOMOP_INTERNAL_DIR_NAME)
        file = "mj_preparation.log"
        try:
            os.makedirs(mj_config_path_conf, exist_ok=True)
            with open(os.path.join(mj_config_path_conf, file), 'w') as fd:
                if len(err) > 0:
                    fd.write("Errors in MJ preparation:\n")
                    for e in err:
                        fd.write(e + "\n")
                else:
                    fd.write("MJ preparation - OK.\n")
        except (RuntimeError, IOError):
            pass
        if len(err) > 0:
            mj = self._data_app.multijobs[mj_id]
            mj.state.status = TaskStatus.error
            mj.state.update_time = time.time()
            self._mj_changed_state.add(mj_id)
            return

        # start MJ
        answer = []
        self._backend_proxy.call("request_start_mj", {"mj_id": mj_id, "mj_conf": mj_conf}, answer)

    def mj_stop(self, mj_id):
        """Stop multijob"""
        answer = []
        self._backend_proxy.call("request_stop_mj", mj_id, answer)

    def mj_delete(self, mj_id):
        """Delete multijob"""
        answer = []
        self._backend_proxy.call("request_delete_mj", mj_id, answer)
        self._answers_from_delete.append((mj_id, answer))

    def download_whole_mj(self, mj_id):
        """Downloads whole multijob"""
        answer = []
        self._backend_proxy.call("request_download_whole_mj", mj_id, answer)
        self._answers_from_download.append((mj_id, answer))

    def get_mj_changed_state(self):
        """
        Returns list of MJ which changed state, from last call this method.
        :return:
        """
        ret = list(self._mj_changed_state)
        self._mj_changed_state.clear()
        return ret

    def get_mj_delegator_online(self):
        """Returns dict of MJ delegator online"""
        return {k: v.delegator_online for k, v in self._mj_report.items()}

    def ssh_test(self, ssh):
        """Performs ssh test"""
        ssh_conf = config_builder.build_ssh_conf(ssh)
        answer = []
        self._backend_proxy.call("request_ssh_test", ssh_conf, answer)
        return answer
