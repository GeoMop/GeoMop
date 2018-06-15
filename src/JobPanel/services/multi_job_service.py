import sys
import os
import logging
import json
import traceback
import enum
import shutil
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))

from JobPanel.backend.service_base import ServiceBase, ServiceStatus, LongRequest
from JobPanel.backend.json_data import JsonData, ClassFactory, JsonDataNoConstruct
from JobPanel.backend.connection import ConnectionStatus, SSHError
from Analysis.pipeline.pipeline_processor import Pipelineprocessor
from Analysis.pipeline import *


class MJStatus(enum.IntEnum):
    """
    State of a multi job.
    """
    preparing = 1
    running = 2
    success = 3
    error = 4
    stopping = 5


class JobStatus(enum.IntEnum):
    """
    State of a job.
    """
    starting = 1
    queued = 2
    running = 3
    downloading_result = 4
    done = 5
    error = 6
    stopped = 7


class JobInfo:
    """
    Job info struct.
    """
    def __init__(self, runner, results_start_child, job_dir):
        self.status = JobStatus.starting
        self.runner = runner
        self.results_start_child = results_start_child
        self.results_download_job_result = None
        self.child_id = None
        self.job_dir = job_dir


class JobReport(JsonData):
    """
    Crate for store job report information.
    """
    def __init__(self, config={}):
        self.status = JobStatus.starting
        self.name = ""
        self.insert_time = 0.0
        self.queued_time = 0.0
        self.start_time = 0.0
        self.done_time = 0.0

        super().__init__(config)

    # def __eq__(self, other):
    #     if isinstance(other, JobReport):
    #         return self.status == other.status and \
    #             self.name == other.name and \
    #             self.insert_time == other.insert_time and \
    #             self.queued_time == other.queued_time and \
    #             self.start_time == other.start_time and \
    #             self.done_time == other.done_time
    #     else:
    #         return NotImplemented


class MultiJob(ServiceBase):
    def __init__(self, config):
        self.pipeline = {"python_script": "",
                         "pipeline_name": ""}
        """pipeline description"""

        self.job_service_data = JsonDataNoConstruct()
        """job service data template"""

        self.mj_status = MJStatus.preparing
        """inner status of multi job"""

        self.max_n_jobs = 10
        """maximal count of running jobs"""

        self.jobs_report = JsonDataNoConstruct()
        """jobs report information"""

        super().__init__(config)

        # JsonData dict workaround
        self.jobs_report = JsonData.construct_dict(JobReport(), self.jobs_report)

        self._pipeline_processor = None

        self._jobs = {}
        self._max_job_id = 0
        self._n_running_jobs = 0

        self._config_changed = False
        self._last_config_saved = 0.0

        self._counter = 0

    def _do_work(self):
        if self.status == ServiceStatus.done:
            return

        # preparing
        if self.mj_status == MJStatus.preparing:
            logging.info("Run pipeline")
            self.run_pipeline()
            if self.mj_status != MJStatus.error:
                self.mj_status = MJStatus.running

        # running
        elif self.mj_status == MJStatus.running:
            self.check_jobs()
            if self._pipeline_processor.is_run():
                self._counter += 1
                if self._counter >= 10:
                    if self._n_running_jobs < self.max_n_jobs:
                        runner = self._pipeline_processor.get_next_job()
                        if runner is not None:
                            self.run_job(runner)
                    self._counter = 0
            else:
                if len(self._jobs) == 0:
                    assert self._n_running_jobs == 0
                    self.mj_status = MJStatus.success

        # success
        elif self.mj_status == MJStatus.success:
            self._set_status_done()

        # error, stopping
        elif self.mj_status in [MJStatus.error, MJStatus.stopping]:
            self.check_jobs()
            if len(self._jobs) == 0:
                self._set_status_done()

        # save config if needed
        if self._config_changed and (time.time() > self._last_config_saved + 10):
            self.save_config()
            self._config_changed = False
            self._last_config_saved = time.time()

    def run_pipeline(self):
        # run script
        try:
            with open(self.pipeline["python_script"], 'r') as fd:
                script_text = fd.read()
        except (RuntimeError, IOError) as e:
            logging.error("Can't open script file: {0}".format(e))
            self.mj_status == MJStatus.error
            return
        action_types.__action_counter__ = 0
        loc = {}
        exec(script_text, globals(), loc)
        pipeline = loc[self.pipeline["pipeline_name"]]

        # pipeline processor
        self._pipeline_processor = Pipelineprocessor(pipeline)

        # validation
        err = self._pipeline_processor.validate()
        if len(err) > 0:
            for e in err:
                logging.error(e)
            self.mj_status = MJStatus.error
            return

        # run pipeline
        self._pipeline_processor.run()

    def run_job(self, runner):
        # job data
        service_data = self.job_service_data.copy()

        # job_service_executable
        job_service_executable = None
        for e in service_data["service_host_connection"]["environment"]["executables"]:
            if e["name"] == "job_service":
                job_service_executable = e
                break
        if job_service_executable is None:
            logging.error("Unable to find executable: {}".format("job_service"))
            self.mj_status == MJStatus.error
        service_data["process"] = service_data["process"].copy()
        service_data["process"]["executable"] = job_service_executable

        # job_executable
        job_executable = None
        name = runner.command[0]
        for e in service_data["service_host_connection"]["environment"]["executables"]:
            if e["name"] == name:
                job_executable = e
                break
        if job_executable is None:
            #logging.error("Unable to find executable: {}".format(name))
            #self.mj_status == MJStatus.error
            job_executable = {"__class__": "Executable",
                              "name": name,
                              "path": ""}
        service_data["job_executable"] = job_executable

        # job_exec_args
        service_data["job_exec_args"] = {"__class__": "ExecArgs",
                                         "args": runner.command[1:]}

        # job_id
        self._max_job_id += 1
        job_id = self._max_job_id

        # job workspace
        job_dir = os.path.join(self.workspace, "job_{}".format(job_id))
        analysis_workspace = self.service_host_connection.environment.geomop_analysis_workspace
        os.makedirs(os.path.join(analysis_workspace, job_dir), exist_ok=True)
        service_data["workspace"] = job_dir

        service_data["config_file_name"] = "job_service.conf"

        # copy action input files
        for file in runner.input_files:
            src = os.path.join(analysis_workspace, self.workspace, file)
            dst = os.path.join(analysis_workspace, job_dir, file)
            shutil.copyfile(src, dst)

        # input_files
        if "input_files" in service_data:
            service_data["input_files"].append(runner.input_files)
        else:
            service_data["input_files"] = runner.input_files

        # update service_host_connection
        if service_data["process"]["__class__"] == "ProcessPBS" and \
                service_data["service_host_connection"]["__class__"] == "ConnectionLocal" and \
                service_data["service_host_connection"]["address"] == "localhost":
            service_data["service_host_connection"] = service_data["service_host_connection"].copy()
            service_data["service_host_connection"]["address"] = self.listen_address[0]

        # start job
        logging.info("Job {} starting".format(job_id))
        answer = []
        self.call("request_start_child", service_data, answer)
        job_info = JobInfo(runner, answer, job_dir)
        self._jobs[job_id] = job_info
        self._n_running_jobs += 1

        # update job report
        job_report = JobReport()
        job_report.status = job_info.status
        job_report.name = "job_{}".format(job_id)
        job_report.insert_time = time.time()
        self.jobs_report[str(job_id)] = job_report

    def check_jobs(self):
        """
        Check jobs and update status.
        :return:
        """
        for job_id in list(self._jobs.keys()):
            job_info = self._jobs[job_id]
            job_report = self.jobs_report[str(job_id)]

            # starting
            if job_info.status == JobStatus.starting:
                if len(job_info.results_start_child) > 0:
                    res = job_info.results_start_child[-1]
                    if "error" in res:
                        logging.error("Unable to start job {}".format(job_id))
                        self._n_running_jobs -= 1
                        assert self._n_running_jobs >= 0
                        job_info.status = JobStatus.error
                        self.mj_status = MJStatus.error
                        del self._jobs[job_id]
                    else:
                        job_info.child_id = res["data"]
                        job_info.status = JobStatus.queued
                        job_report.queued_time = time.time()
                    job_report.status = job_info.status
                    self._config_changed = True

            # queued
            elif job_info.status == JobStatus.queued:
                proxy = self._child_services[job_info.child_id]
                if proxy._status == ServiceStatus.queued:
                    if proxy.stopped:
                        proxy.close()
                        with self._child_services_lock:
                            del self._child_services[job_info.child_id]
                        self._n_running_jobs -= 1
                        assert self._n_running_jobs >= 0

                        job_info.status = JobStatus.stopped
                        del self._jobs[job_id]
                        #job_report.done_time = time.time()
                        self._config_changed = True

                        job_report.status = job_info.status
                    elif self.mj_status == MJStatus.stopping:
                        proxy.stop()
                # todo: vyresit situaci, kdy pri zabijeni sluzby, ta prejde do stavu running
                elif proxy._status in [ServiceStatus.running, ServiceStatus.done]:
                    job_info.status = JobStatus.running
                    job_report.status = job_info.status
                    job_report.start_time = time.time()
                    self._config_changed = True

            # running
            elif job_info.status == JobStatus.running:
                proxy = self._child_services[job_info.child_id]
                if proxy._status == ServiceStatus.running:
                    if proxy.stopped:
                        proxy.close()
                        with self._child_services_lock:
                            del self._child_services[job_info.child_id]
                        self._n_running_jobs -= 1
                        assert self._n_running_jobs >= 0

                        job_info.status = JobStatus.stopped
                        del self._jobs[job_id]
                        #job_report.done_time = time.time()
                        self._config_changed = True

                        job_report.status = job_info.status
                    elif self.mj_status == MJStatus.stopping:
                        proxy.stop()
                elif proxy._status == ServiceStatus.done:
                    conf = proxy._downloaded_config
                    if (conf is not None) and (ServiceStatus[conf["status"]] == ServiceStatus.done):
                        proxy.close()
                        with self._child_services_lock:
                            del self._child_services[job_info.child_id]
                        self._n_running_jobs -= 1
                        assert self._n_running_jobs >= 0

                        if conf["error"]:
                            job_info.status = JobStatus.error
                            del self._jobs[job_id]
                            job_report.done_time = time.time()
                            self._config_changed = True
                        elif conf["stopping"]:
                            job_info.status = JobStatus.stopped
                            del self._jobs[job_id]
                            job_report.done_time = time.time()
                            self._config_changed = True
                        else:
                            logging.info("Job {} downloading result".format(job_id))
                            job_info.results_download_job_result = []
                            self.call("request_download_job_result", job_id, job_info.results_download_job_result)
                            job_info.status = JobStatus.downloading_result
                        job_report.status = job_info.status

            # downloading
            elif job_info.status == JobStatus.downloading_result:
                if len(job_info.results_download_job_result) > 0:
                    res = job_info.results_download_job_result[-1]
                    if ("error" in res) or (not res["data"]):
                        # todo: pokud se stahovani nezdarilo z duvodu nefunkcniho connection, melo by se stahovani opakovat
                        logging.error("Job {} unable download result".format(job_id))
                        job_info.status = JobStatus.error
                        self.mj_status = MJStatus.error
                    else:
                        self._pipeline_processor.set_job_finished(job_info.runner.id)
                        job_info.status = JobStatus.done
                    del self._jobs[job_id]
                    job_report.status = job_info.status
                    job_report.done_time = time.time()
                    self._config_changed = True

    @LongRequest
    def request_download_job_result(self, job_id):
        """
        Downloads job result files.
        :param job_id:
        :return:
        """
        loc_an_work = self.service_host_connection.environment.geomop_analysis_workspace
        rem_an_work = self.job_service_data["service_host_connection"]["environment"]["geomop_analysis_workspace"]
        con = self.get_connection(self.job_service_data["service_host_connection"])
        if con._status != ConnectionStatus.online:
            return False
        try:
            # output files
            con.download(self._jobs[job_id].runner.output_files,
                         os.path.join(loc_an_work, self.workspace),
                         os.path.join(rem_an_work, self._jobs[job_id].job_dir))

            # log file
            con.download([os.path.join(self._jobs[job_id].job_dir, "job_service.log")],
                         loc_an_work,
                         rem_an_work)
        except (SSHError, FileNotFoundError, PermissionError):
            return False
        return True

    def request_get_jobs_report(self, job_id_list):
        """
        Return jobs report for jobs their ids are in job_id_list.
        :param job_id_list:
        :return:
        """
        reports = {}
        for id in job_id_list:
            if id in self.jobs_report:
                reports[id] = self.jobs_report[id].serialize()
        return {"reports": reports, "n_jobs": len(self.jobs_report)}

    def request_stop(self, data):
        if self.mj_status != MJStatus.stopping:
            self.mj_status = MJStatus.stopping
            self._config_changed = True
        # todo: backend se zmenu statusu nemusi dozvedet, pokud je MJ online .conf soubor se pravidelne nestahuje
        return {'data': 'closing'}


if __name__ == "__main__":
    logging.basicConfig(filename='mj_service.log', filemode="w",
                        format='%(asctime)s %(levelname)-8s %(name)-12s %(message)s',
                        level=logging.INFO)


    try:
        input_file = "mj_service.conf"
        with open(input_file, "r") as f:
            config = json.load(f)
        bs = MultiJob(config)
        bs.run()
    except:
        logging.error("Uncatch exception:\n" + "".join(traceback.format_exception(*sys.exc_info())))
        raise
