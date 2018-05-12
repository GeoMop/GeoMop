import sys
import os
import logging
import traceback
import json
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

from backend.service_base import ServiceBase, LongRequest, ServiceStatus
from backend.json_data import JsonData, JsonDataNoConstruct
from backend.service_proxy import ServiceProxy
from services.multi_job_service import JobReport, JobStatus, MJStatus
from data.states import TaskStatus as GuiTaskStatus
from backend.connection import ConnectionStatus, SSHError


class MJInfo(JsonData):
    """
    MJ info struct.
    """
    def __init__(self, config={}):
        self.proxy = ServiceProxy()
        """mj proxy"""

        self.n_jobs = 0
        """number of known jobs"""

        self.queued_time = 0.0
        """MJ queued time"""

        self.files_to_download = []
        """Files need to be downloaded"""

        self.log_planed_to_download = False
        """True if log file was planed to download"""

        self.job_log_planed_to_download = []
        """List of job names which has their log planed to download"""

        self.jobs_report_save_counter = 0
        """jobs report save counter"""

        super().__init__(config)

        self._jobs_report = {}
        """jobs report information"""

        self._results_get_jobs_report = []
        """Result list of get jobs report request"""

        self._jobs_report_time = 0.0
        """Last time request_get_jobs_report sent or report retrieved from proxy._downloaded_config"""


class MJReport(JsonData):
    """
    Crate for store MJ report information.
    """
    def __init__(self, config={}):
        self.service_status = ServiceStatus.queued
        self.mj_status = MJStatus.preparing
        self.proxy_stopping = False
        self.proxy_stopped = False
        self.queued_time = 0.0
        self.start_time = 0.0
        self.done_time = 0.0
        self.known_jobs = 0
        self.estimated_jobs = 0
        self.finished_jobs = 0
        self.running_jobs = 0
        self.jobs_report_save_counter = 0

        super().__init__(config)

    def __eq__(self, other):
        if isinstance(other, MJReport):
            return self.service_status == other.service_status and \
                self.mj_status == other.mj_status and \
                self.proxy_stopping == other.proxy_stopping and \
                self.proxy_stopped == other.proxy_stopped and \
                self.queued_time == other.queued_time and \
                self.start_time == other.start_time and \
                self.done_time == other.done_time and \
                self.known_jobs == other.known_jobs and \
                self.estimated_jobs == other.estimated_jobs and \
                self.finished_jobs == other.finished_jobs and \
                self.running_jobs == other.running_jobs and \
                self.jobs_report_save_counter == other.jobs_report_save_counter
        else:
            return NotImplemented


class Backend(ServiceBase):
    """
    """

    def __init__(self, config):
        self.mj_info = JsonDataNoConstruct()
        """dict of managed MJ information"""

        # find repeater_max_client_id
        repeater_max_client_id = 0
        if "mj_info" in config:
            for mj in config["mj_info"].values():
                child_id = mj["proxy"]["child_id"]
                if child_id > repeater_max_client_id:
                    repeater_max_client_id = child_id

        super().__init__(config, repeater_max_client_id)

        # JsonData dict workaround
        self.mj_info = JsonData.construct_dict(MJInfo(), self.mj_info)

        self._new_mj_queue = []
        """Queue with new MJ to add to self.mj_info"""
        self._delete_mj_queue = []
        """Queue with MJ to delete from self.mj_info"""

        self._config_changed = False
        self._last_config_saved = 0.0

        self._proxies_resuscitated = False

    def _do_work(self):
        if not self._proxies_resuscitated:
            self._resuscitate_proxies()

        self._retrieve_jobs_report()
        self._download_files()
        self._check_mj_status()
        self._process_queues()

        # save config if needed
        if self._config_changed and (time.time() > self._last_config_saved + 1):
            self.save_config()
            self._config_changed = False
            self._last_config_saved = time.time()

    def _resuscitate_proxies(self):
        """
        Calls _request_resuscitate_proxy for all deserialized proxies.
        :return:
        """
        for mj in self.mj_info.values():
            proxy = mj.proxy
            answer = []
            self.call("_request_resuscitate_proxy", proxy, answer)
        self._proxies_resuscitated = True

    @LongRequest
    def _request_resuscitate_proxy(self, proxy):
        """
        Gets connection and connect service.
        :param proxy:
        :return:
        """
        # todo: je potreba nastavit heslo
        # todo: v get_connection muze nastat chyba
        con = self.get_connection(proxy.connection_config)
        proxy.set_rep_con(self._repeater, con)
        proxy.connect_service()
        with self._child_services_lock:
            self._child_services[proxy.child_id] = proxy

    def _retrieve_jobs_report(self):
        """
        Retrieves Jobs report data.
        :return:
        """
        for mj in self.mj_info.values():
            # result
            while len(mj._results_get_jobs_report) > 0:
                res = mj._results_get_jobs_report.pop(0)
                if "error" in res:
                    logging.error("Error in retrieving Jobs report")
                else:
                    jobs_report = res["data"]
                    mj.n_jobs = jobs_report["n_jobs"]
                    new_jobs_report = JsonData.construct_dict(JobReport(), jobs_report["reports"])
                    self._update_jobs_report(mj, new_jobs_report)

            if time.time() > mj._jobs_report_time + 2:
                if mj.proxy._online:
                    # send request
                    job_id_list = []
                    for i in range(1, mj.n_jobs + 1):
                        id = str(i)
                        if (id not in mj._jobs_report) or \
                                (mj._jobs_report[id].status not in [JobStatus.done, JobStatus.error]):
                            job_id_list.append(id)
                    mj.proxy.call("request_get_jobs_report", job_id_list, mj._results_get_jobs_report)
                else:
                    # get data from config file
                    conf = mj.proxy._downloaded_config
                    if (conf is not None) and ("jobs_report" in conf):
                        new_n_jobs = len(conf["jobs_report"])
                        if new_n_jobs > mj.n_jobs:
                            mj.n_jobs = new_n_jobs
                        new_jobs_report = JsonData.construct_dict(JobReport(), conf["jobs_report"])
                        self._update_jobs_report(mj, new_jobs_report)
                mj._jobs_report_time = time.time()

    def _update_jobs_report(self, mj, new_jobs_report):
        """
        Updates jobs report with new information.
        :param mj:
        :param new_jobs_report:
        :return:
        """
        changed = False
        for k, v in new_jobs_report.items():
            if (k not in mj._jobs_report) or (v.status > mj._jobs_report[k].status):
                mj._jobs_report[k] = v
                changed = True

                if (v.status in [JobStatus.done, JobStatus.error]) and (v.name not in mj.job_log_planed_to_download):
                    mj.files_to_download.append(os.path.join(v.name, "job_service.log"))
                    mj.job_log_planed_to_download.append(v.name)

            # We need update run_interval
            if v.status in [JobStatus.running, JobStatus.downloading_result]:
                changed = True
        if changed:
            self._save_jobs_states(mj)
            mj.jobs_report_save_counter += 1
            self._config_changed = True

    def _save_jobs_states(self, mj):
        """
        Saves MJ jobs status to file.
        :param mj:
        :return:
        """
        jobs_states = []
        for k, v in mj._jobs_report.items():
            # status
            status = GuiTaskStatus.none
            if v.status in [JobStatus.starting, JobStatus.queued]:
                status = GuiTaskStatus.queued
            elif v.status in [JobStatus.running, JobStatus.downloading_result]:
                status = GuiTaskStatus.running
            elif v.status == JobStatus.done:
                status = GuiTaskStatus.finished
            elif v.status == JobStatus.error:
                status = GuiTaskStatus.error
            elif v.status == JobStatus.stopped:
                status = GuiTaskStatus.stopped

            # run_interval
            run_interval = 0.0
            if v.done_time:
                run_interval = v.done_time - v.start_time
            elif v.start_time:
                run_interval = time.time() - v.start_time

            d = {"status": status,
                 "name": v.name,
                 "insert_time": v.insert_time,
                 "queued_time": v.queued_time,
                 "start_time": v.start_time,
                 "run_interval": run_interval}
            jobs_states.append(d)

        # save to file
        dir = os.path.join(self.get_analysis_workspace(),
                           mj.proxy.workspace,
                           "..", "res", "state")
        os.makedirs(dir, exist_ok=True)
        file = os.path.join(dir, "jobs_states.json")
        try:
            with open(file, 'w') as fd:
                json.dump(jobs_states, fd, indent=4, sort_keys=True)
        except Exception as e:
            logging.error("Jobs states saving error: {0}".format(e))

    def _download_files(self):
        """
        Download files which are in self.files_to_download.
        :return:
        """
        # todo: predelat tak, aby probihalo ve vlakne, kazdy MJ bude mit svoje stahovaci vlakno
        for mj in self.mj_info.values():
            con = mj.proxy._connection
            if (con is not None) and (con._status == ConnectionStatus.online):
                while len(mj.files_to_download) > 0:
                    try:
                        con.download(
                            [mj.files_to_download[0]],
                            os.path.join(self.get_analysis_workspace(), mj.proxy.workspace),
                            os.path.join(con.environment.geomop_analysis_workspace, mj.proxy.workspace))
                        del mj.files_to_download[0]
                        # todo: az bude ve vlakne, bude se muset pouzit zamek nebo resit pres queue - to je asi lepsi
                        self._config_changed = True
                    except SSHError as e:
                        logging.error("Downloading file error: {0}".format(e))
                        break
                    except (FileNotFoundError, PermissionError) as e:
                        logging.error("Downloading file error: {0}".format(e))
                        del mj.files_to_download[0]
                        self._config_changed = True

    def _check_mj_status(self):
        """
        Check MJ status and perform appropriate action.
        :return:
        """
        for mj in self.mj_info.values():
            if mj.proxy._status == ServiceStatus.done and not mj.log_planed_to_download:
                mj.files_to_download.append("mj_service.log")
                mj.log_planed_to_download = True

    def _process_queues(self):
        """
        Process requests from other threads.
        :return:
        """
        for i in range(len(self._new_mj_queue)):
            mj_id, mj = self._new_mj_queue.pop(0)
            self.mj_info[mj_id] = mj
            self._config_changed = True

        for i in range(len(self._delete_mj_queue)):
            mj_id = self._delete_mj_queue.pop(0)
            mj = self.mj_info[mj_id]
            mj.proxy.close()
            with self._child_services_lock:
                del self._child_services[mj.proxy.child_id]
            del self.mj_info[mj_id]
            self._config_changed = True

    """ Backend requests. """

    @LongRequest
    def request_start_mj(self, data):
        """
        Starts MJ.
        :param data: dict with keys "mj_id" and "mj_conf"
        :return:
        """
        mj_id = data["mj_id"]
        mj_conf = data["mj_conf"]
        child_id = self.request_start_child(mj_conf)
        mj = MJInfo()
        with self._child_services_lock:
            mj.proxy = self._child_services[child_id]
        mj.queued_time = time.time()
        self._new_mj_queue.append((mj_id, mj))

    def request_stop_mj(self, mj_id):
        """
        Stops MJ.
        :param mj_id:
        :return:
        """
        # todo: Pokud MJ zkolaboval je potreba zastavit Joby.
        if mj_id not in self.mj_info:
            logging.warning("Attempt to stop nonexistent MJ.")
            return
        mj = self.mj_info[mj_id]
        mj.proxy.stop()

    @LongRequest
    def request_delete_mj(self, mj_id):
        """
        Deletes MJ.
        :param mj_id:
        :return: str with error or None
        """
        if mj_id not in self.mj_info:
            logging.warning("Attempt to delete nonexistent MJ.")
            return None
        mj = self.mj_info[mj_id]

        mj_dir = mj.proxy.workspace
        if os.path.basename(mj_dir) == "mj_config":
            mj_dir = os.path.dirname(mj_dir)

        # delete MJ remote data
        con = mj.proxy._connection
        if (con is not None) and (con._status == ConnectionStatus.online):
            try:
                con.delete(
                    [mj_dir],
                    con.environment.geomop_analysis_workspace)
            except (SSHError, PermissionError):
                return "Unable to delete MJ remote data, PermissionError."
            except FileNotFoundError:
                pass
        else:
            return "Unable to delete MJ remote data, connection is offline."

        # delete Job remote data
        conf = mj.proxy._downloaded_config
        if conf is not None:
            con_data = conf["job_service_data"]["service_host_connection"]
            if con_data["__class__"] == "ConnectionSSH":
                try:
                    con = self.get_connection(con_data)
                except SSHError:
                    return "Unable to delete Job remote data, ssh connection error."
                if con._status == ConnectionStatus.online:
                    try:
                        con.delete(
                            [mj_dir],
                            con.environment.geomop_analysis_workspace)
                    except (SSHError, PermissionError):
                        return "Unable to delete Job remote data, PermissionError."
                    except FileNotFoundError:
                        pass
                else:
                    return "Unable to delete Job remote data, connection is offline."
        else:
            return "Unable to delete Job remote data."

        # delete MJInfo
        self._delete_mj_queue.append(mj_id)
        while(mj_id in self.mj_info):
            time.sleep(0.1)

        return None

    def request_get_mj_report(self, data):
        """
        Return MJ report.
        :param data:
        :return:
        """
        reports = {}
        for k, mj in self.mj_info.items():
            status = mj.proxy._status
            if status is None:
                continue

            rep = MJReport()
            rep.service_status = status
            rep.proxy_stopping = mj.proxy.stopping
            rep.proxy_stopped = mj.proxy.stopped
            rep.known_jobs = mj.n_jobs
            rep.estimated_jobs = mj.n_jobs
            rep.queued_time = mj.queued_time
            rep.jobs_report_save_counter = mj.jobs_report_save_counter
            for v in mj._jobs_report.values():
                if v.status in [JobStatus.running, JobStatus.downloading_result]:
                    rep.running_jobs += 1
                elif v.status in [JobStatus.done, JobStatus.error]:
                    rep.finished_jobs += 1

            conf = mj.proxy._downloaded_config
            if (conf is not None) and (ServiceStatus[conf["status"]] == status):
                if "start_time" in conf:
                    rep.start_time = conf["start_time"]
                if "done_time" in conf:
                    rep.done_time = conf["done_time"]
                if "mj_status" in conf:
                    rep.mj_status = MJStatus[conf["mj_status"]]

            reports[str(k)] = rep.serialize()
        return reports

    @LongRequest
    def request_download_whole_mj(self, mj_id):
        """
        Downloads whole MJ from remote.
        :param data:
        :return:
        """
        if mj_id not in self.mj_info:
            logging.warning("Attempt to download nonexistent MJ.")
            return
        mj = self.mj_info[mj_id]
        con = mj.proxy._connection
        if con._status == ConnectionStatus.online:
            dir = os.path.join(self.get_analysis_workspace(),
                               mj.proxy.workspace,
                               "..", "downloaded_config")
            os.makedirs(dir, exist_ok=True)
            try:
                con.download(
                    ["mj_config"],
                    dir,
                    os.path.join(con.environment.geomop_analysis_workspace, mj.proxy.workspace, ".."))
            except (SSHError, FileNotFoundError, PermissionError):
                pass


##########
# Main body
##########


if __name__ == "__main__":
    logging.basicConfig(filename='backend_service.log', filemode="w",
                        format='%(asctime)s %(levelname)-8s %(name)-12s %(message)s',
                        level=logging.INFO)


    try:
        input_file = "backend_service.conf"
        with open(input_file, "r") as f:
            config = json.load(f)
        bs = Backend(config)
        bs.run()
    except:
        logging.error("Uncatch exception:\n" + "".join(traceback.format_exception(*sys.exc_info())))
        raise
