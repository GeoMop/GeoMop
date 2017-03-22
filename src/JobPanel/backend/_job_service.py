"""
Starting point of the job_service.
Usage: python3 job_service.py [config.json]
"""
import sys
import service_base
import logging
import threading

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
        self.parent_port=9123
        self.job_parameters = {}
        """
        Common and PBS job parameters.
        """
        self.environment=Environment()
        self.executable=""
        self.exec_args=""
        super().__init__(config)

        # can not work this way, how we get return value
        # instead we must have mechanism how to call in threads and store results with requests, then we can use
        # this mechanism for both requests and own functions.
        self.requests.append( {'action': "execute" } )
        self.connect_parent()

    @LongRequest
    def execute(self):
        """
        This request is called by Job itself.
        :return:
        """




def job_main():
    input_file = "job_config.json"
    if len(sys.argv) >  1:
        input_file = sys.argv[1]
    with open(input_file, "r") as f:
        config = json.load(f)
    job = Job(config)
    job.poll()


if __name__ == "__main__":

    logger=logging.Logger("job_main")
    try:
        job_main()
    except Exception as err:
        logger.error(err))
        sys.exit(ServiceExit.1)

