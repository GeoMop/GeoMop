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

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

from backend import service_base
from backend.executor import Executable, ExecArgs


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
        super().__init__(config)

        # can not work this way, how we get return value
        # instead we must have mechanism how to call in threads and store results with requests, then we can use
        # this mechanism for both requests and own functions.
        #self.requests.append( {'action': "execute" } )
        #self.connect_parent()

        if self.job_exec_args.work_dir == "":
            self.job_exec_args.work_dir = self.workspace

        self._job_thread = None

    def _job_run(self):
        args = []
        if self.job_executable.script:
            args.append(self.process.environment.python)
        args.append(os.path.join(self.process.environment.geomop_root,
                                 self.job_executable.path,
                                 self.job_executable.name))
        args.extend(self.job_exec_args.args)
        cwd = os.path.join(self.process.environment.geomop_analysis_workspace,
                           self.job_exec_args.work_dir)
        with open(os.path.join(cwd, "job_out.txt"), 'w') as fd_out:
            p = psutil.Popen(args, stdout=fd_out, stderr=subprocess.STDOUT, cwd=cwd)
            p.wait()

    def _do_work(self):
        if self._job_thread is None:
            self._job_thread = threading.Thread(target=self._job_run, daemon=True)
            self._job_thread.start()
        elif not self._job_thread.is_alive():
            self.status = service_base.ServiceStatus.done
            self.save_config()
            self._closing = True


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

    # logger=logging.Logger("job_main")
    # try:
    #     job_main()
    # except Exception as err:
    #     logger.error(err))
    #     sys.exit(ServiceExit.1)

    logging.basicConfig(filename='job_service.log', filemode="w",
                        format='%(asctime)s %(levelname)-8s %(name)-12s %(message)s',
                        level=logging.INFO)

    try:
        job_main()
    except:
        logging.error("Uncatch exception:\n" + "".join(traceback.format_exception(*sys.exc_info())))
        raise
