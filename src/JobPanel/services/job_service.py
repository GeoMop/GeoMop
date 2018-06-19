"""
Starting point of the job_service.
Usage: python3 job_service.py [config.json]
"""
import sys
import os
import logging
import threading
import json
import traceback
import psutil
import subprocess
import time
import random

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))

from JobPanel.backend import service_base
from JobPanel.backend.executor import Executable, ExecArgs


"""
Assuming ServiceBase.thread_pool

from multiprocessing.pool import ThreadPool
pool = ThreadPool(processes=10)

and
ServideBase.run_in_thread(fun, args, result):
    async_result = pool.apply_async(foo, ('world', 'foo')) # tuple of args for foo

# do some other stuff in the main process

return_val = async_result.get()  # get the return value from your function.
"""

class Job(service_base.ServiceBase):
    def __init__(self, config):
        #self.parent_port=9123
        #self.job_parameters = {}
        """
        Common and PBS job parameters.
        """
        #self.environment=Environment()
        self.job_executable=Executable()
        self.job_exec_args=ExecArgs()

        self.error = False
        """If error occurs."""
        self.stopping = False
        """If stopping was requested."""

        super().__init__(config)

        # can not work this way, how we get return value
        # instead we must have mechanism how to call in threads and store results with requests, then we can use
        # this mechanism for both requests and own functions.
        #self.requests.append( {'action': "execute" } )
        #self.connect_parent()

        if self.job_exec_args.work_dir == "":
            self.job_exec_args.work_dir = self.workspace

        self._job_thread = None

        # for testing purposes only
        #self.wait_before_run = random.randrange(0, 30)

    def _job_run(self):
        # find executable
        if self.job_executable.path == "":
            executables = self.request_get_executables_from_installation()
            if executables is None:
                logging.error("Unable to load installation executables.")
                self.error = True
                return
            job_executable = None
            name = self.job_executable.name
            for e in executables:
                if e["name"] == name:
                    job_executable = e
                    break
            if job_executable is None:
                logging.error("Unable to find executable: {}".format(name))
                self.error = True
                return
            if "__class__" in job_executable:
                del job_executable["__class__"]
            self.job_executable = Executable(job_executable)

        args = []
        if self.job_executable.script:
            args.append(self.process.environment.python)
        args.append(os.path.join(self.process.environment.geomop_root,
                                 self.job_executable.path))
        args.extend(self.job_exec_args.args)
        cwd = os.path.join(self.process.environment.geomop_analysis_workspace,
                           self.job_exec_args.work_dir)
        with open(os.path.join(cwd, "job_out.txt"), 'w') as fd_out:
            p = psutil.Popen(args, stdout=fd_out, stderr=subprocess.STDOUT, cwd=cwd)
            while not self.stopping:
                try:
                    p.wait(1)
                    break
                except psutil.TimeoutExpired:
                    continue
            try:
                p.terminate()
            except psutil.NoSuchProcess:
                pass
            else:
                try:
                    p.wait(1)
                except psutil.TimeoutExpired:
                    try:
                        p.kill()
                    except psutil.NoSuchProcess:
                        pass
                    else:
                        try:
                            p.wait(1)
                        except psutil.TimeoutExpired:
                            logging.error("Unable to kill Job's process. PID: {}".format(p.pid))
                            self.error = True

        # for testing purposes only
        # end_time = time.time() + random.randrange(0, 30)
        # while (not self.stopping) and (time.time() < end_time):
        #     time.sleep(0.1)

    def _do_work(self):
        if self._job_thread is None:
            self._job_thread = threading.Thread(target=self._job_run, daemon=True)
            self._job_thread.start()
        elif not self._job_thread.is_alive():
            self._set_status_done()

    def request_stop(self, data):
        if not self.stopping:
            self.stopping = True
            self.save_config()
        return {'data': 'closing'}


def job_main():
    input_file = "job_service.conf"
    if len(sys.argv) >  1:
        input_file = sys.argv[1]
    with open(input_file, "r") as f:
        config = json.load(f)
    job = Job(config)
    job.run()
    #time.sleep(10)


if __name__ == "__main__":
    logging.basicConfig(filename='job_service.log', filemode="w",
                        format='%(asctime)s %(levelname)-8s %(name)-12s %(message)s',
                        level=logging.INFO)

    try:
        job_main()
    except:
        logging.error("Uncatch exception:\n" + "".join(traceback.format_exception(*sys.exc_info())))
        raise
