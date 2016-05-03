"""Pipeline help function for internall using in tak JobScheduler only"""

class PipelineStatistics:
    def __init__(self):
        self.known_jobs = 0
        """count of known jobs (minimal amount of jobs)"""
        self.estimated_jobs = 0
        """estimated count of jobs"""
        self.finished_jobs = 0
        """count of finished jobs"""
        self.running_jobs = 0
        """count of running jobs"""

class Pipelineprocessor():
    """
    Class for pipeline processing.
    
    This class contain pipeline action and
    process some job above it as is getting
    pipeline python script, pipeline validation
    and returning pipeline statiscics.
  
    Pipeline processing can be stated by run
    function and stoped by stop function. If pipeline
    is started, get_next_job function return next
    action runner job, that can be processed. After
    job processing is nessery call function 
    set_job_finished(). If not any job is available,
    get_next_job return None.
    """

    def __init__(self,pipeline):
        self._pipeline = pipeline
        """pipeline"""
        self._dependent_actions=[]
        """Actions that depends on other action, that is not still finished"""
        self._wait_actions=[]
        """Independent actions that wait for processing"""
        self._processed_actions=[]
        """Actions that is pass on processing by get_next_job"""
        self._finished_actions=[]
        """
        Actions that is finished. Action is finished if function
        set_job_finished is calld
        """
        self._is_validate = False
        """
        Validation is processed by calling validate function. After validation
        is errs variable set. If is some records in this variable, sepparated
        thread can't be started and run function raise exception. If run
        function is call without validate function, validation is make in run
        internaly.
        """
        self._errs = []
        """validation errors"""
        self._is_run = False
        """Sepparated thread is runed"""
        self._is_finished = False
        """Sepparated thread is finished"""
        self._thread = None

    def get_script(self):
        """return pipeline python script"""
        if not self._is_validate:
            self.validate()
        if len(self._errs) > 0:
            raise Exception("Validation fails, call Validate function for more information.")
        return self._pipeline._get_settings_script()
        
    def validate(self):
        """validate pipeline"""        
        if not self._is_validate:
            return self._errs
        try:
            self._pipeline._inicialize()
            self._errs = self._pipeline._validate()
        except Exception as err:
            self._errs.append("Exception during validation: " + str(err))
        self._is_validate = True
        return self._errs
        
    def run(self):
        """Start pipeline processing in separate thread"""
        if self._is_run:
            return
        if not self._is_validate:
            self.validate()
        if len(self._errs) > 0:
            raise Exception("Validation fails, call Validate function for more information.")        
        
    def stop(self):
        """Terminate pipeline thread and stop procesing"""
        if not self._is_run:
            return

    def get_statistics(self):
        """get pipeline statistics"""
        if not self._is_validate:
            self.validate()
        if len(self._errs) > 0:
            raise Exception("Validation fails, call Validate function for more information.")

    def get_next_job(self):
        """return next job that require externall processing"""
        pass
        
    def set_job_finished(self, job):
        """set job as finished"""
        pass
