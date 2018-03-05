import sys
import os
import logging
import json
import traceback
import enum
import shutil


from ..backend.service_base import ServiceBase, ServiceStatus
from ..backend.json_data import JsonData, ClassFactory, JsonDataNoConstruct
from ..backend.connection import ConnectionStatus, SSHError
from Analysis.pipeline.pipeline_processor import Pipelineprocessor
#from Analysis.pipeline import *


class MJStatus(enum.IntEnum):
    """
    State of a multi job.
    """
    preparing = 1
    running = 2
    success = 3
    error = 4


class JobStatus(enum.IntEnum):
    """
    State of a job.
    """
    starting = 1
    running = 2
    downloading_result = 3
    done = 4
    error = 5


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

        super().__init__(config)

        self._pipeline_processor = None

        self._jobs = {}
        self._max_job_id = 0
        self._n_running_jobs = 0

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
                while self._n_running_jobs < self.max_n_jobs:
                    runner = self._pipeline_processor.get_next_job()
                    if runner is None:
                        break
                    else:
                        self.run_job(runner)
            else:
                if len(self._jobs) == 0:
                    assert self._n_running_jobs == 0
                    self.mj_status = MJStatus.success

        # success
        elif self.mj_status == MJStatus.success:
            self.status = ServiceStatus.done
            self.save_config()
            self._closing = True

        # error
        elif self.mj_status == MJStatus.error:
            self.check_jobs()
            if len(self._jobs) == 0:
                self.status = ServiceStatus.done
                self.save_config()
                self._closing = True

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
        exec(script_text)
        pipeline = locals()[self.pipeline["pipeline_name"]]

        # pipeline processor
        self._pipeline_processor = Pipelineprocessor(pipeline)

        # validation
        err = self._pipeline_processor.validate()
        if len(err) > 0:
            for e in err:
                logging.error(e)
            self.mj_status == MJStatus.error
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
            logging.error("Unable to find executable: {}".format(name))
            self.mj_status == MJStatus.error
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

        # start job
        logging.info("Job {} starting".format(job_id))
        answer = []
        self.call("request_start_child", service_data, answer)
        self._jobs[job_id] = JobInfo(runner, answer, job_dir)
        self._n_running_jobs += 1

    def check_jobs(self):
        """
        Check jobs and update status.
        :return:
        """
        for job_id in list(self._jobs.keys()):
            job_info = self._jobs[job_id]

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
                        job_info.status = JobStatus.running

            # running
            elif job_info.status == JobStatus.running:
                if self._child_services[job_info.child_id].status == ServiceStatus.done:
                    self._child_services[job_info.child_id].close()
                    del self._child_services[job_info.child_id]
                    self._n_running_jobs -= 1
                    assert self._n_running_jobs >= 0

                    logging.info("Job {} downloading result".format(job_id))
                    job_info.results_download_job_result = []
                    self.call("request_download_job_result", job_id, job_info.results_download_job_result)
                    job_info.status = JobStatus.downloading_result

            # downloading
            elif job_info.status == JobStatus.downloading_result:
                if len(job_info.results_download_job_result) > 0:
                    res = job_info.results_download_job_result[-1]
                    if ("error" in res) or (not res["data"]):
                        logging.error("Job {} unable download result {}".format(job_id))
                        job_info.status = JobStatus.error
                        self.mj_status = MJStatus.error
                    else:
                        self._pipeline_processor.set_job_finished(job_info.runner.id)
                        job_info.status = JobStatus.done
                    del self._jobs[job_id]

    # todo: az to bude bezpecne spoustet jako LongRequest
    #@LongRequest
    def request_download_job_result(self, job_id):
        """
        Downloads job result files.
        :param job_id:
        :return:
        """
        analysis_workspace = self.service_host_connection.environment.geomop_analysis_workspace
        local_prefix = os.path.join(analysis_workspace, self.workspace)
        remote_prefix = os.path.join(
            self.job_service_data["service_host_connection"]["environment"]["geomop_analysis_workspace"],
            self._jobs[job_id].job_dir)
        con = self.get_connection(self.job_service_data["service_host_connection"])
        if con._status != ConnectionStatus.online:
            return False
        try:
            con.download(self._jobs[job_id].runner.output_files, local_prefix, remote_prefix)
        except (SSHError, FileNotFoundError, PermissionError):
            return False
        return True


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
