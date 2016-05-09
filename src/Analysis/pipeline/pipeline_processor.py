"""Pipeline help function for internall using in tak JobScheduler only"""
import threading
import time
from .action_types import ActionRunningState

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
    
    !!! all operation with pipeline is done if sepparate
    thread is not run or in run function. Variables
    runners arrays, _stop, pause and _statistics is
    protected by action_lock
    """

    def __init__(self, pipeline):
        self._pipeline = pipeline
        """pipeline"""
        self._complex_runners=[]
        """Runners of independent actions that wait for external processing"""
        self._processed_runners=[]
        """Runners of independent actions that are processing"""
        self._finished_runners=[]
        """Runners of independent actions was processed"""
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
        """
        Sepparated thread is runed.
        (Is start by run function, and is finished prestart preparration)
        """
        self._is_finished = False
        """Sepparated thread is finished and all work is done"""
        self._thread = None
        """Sepparated thread"""
        
        self._statistics = None
        """statiscis"""
        self._action_lock = threading.Lock()
        """lock for runners arrays, _stop, _pause and _statistics variables"""
        self._stop = False
        """signal to sepparate thread for stopping"""
        self._pause = False
        """signal to sepparate thread for pausing"""
        self._run_errs = []
        """errors during run"""

    def get_script(self):
        """return pipeline python script"""
        if not self._is_validate:
            self.validate()
        if len(self._errs) > 0:
            raise Exception("Validation fails, call Validate function for more information.")
        if self.is_run():
            raise Exception("Validation can be make only before running.")
        return self._pipeline._get_settings_script()
        
    def validate(self):
        """validate pipeline"""        
        if self._is_validate:
            return self._errs
        if len(self._errs)>0:
            return self._errs
        try:
            self._pipeline._inicialize()
            self._errs = self._pipeline.validate()
            self._statistics = self._pipeline._get_statistics()
        except Exception as err:
            self._errs.append("Exception during validation: " + str(err))
        self._is_validate = True        
        return self._errs

    def is_run(self):
        """return if if pipeline processor is started"""
        self._action_lock.acquire()
        res = self._is_run
        self._action_lock.release()
        return res
    
    def run(self):
        """Start pipeline processing in separate thread"""
        if self.is_run():
            return
        if not self._is_validate:
            self.validate()
        if len(self._errs) > 0:
            raise Exception("Validation fails, call Validate function for more information.")
        t = threading.Thread(target=self._pipeline_procesing)
        t.daemon = True
        t.start()
        self._is_run = True
        self._stop = False
        
    def stop(self):
        """Terminate pipeline thread and stop procesing"""
        if not self.is_run():
            return
        self._action_lock.acquire()
        self._stop = True
        self._action_lock.release()

    def pause(self, pause):
        """Pause or rerun sepparate thread"""
        if not self.is_run():
            return
        self._action_lock.acquire()
        self._pause = pause
        self._action_lock.release()

    def get_statistics(self):
        """Get pipeline statistics. First statistics are ready after 
        validation"""
        ret = None
        self._action_lock.acquire()
        if self._statistics is not None:
            ret = self._statistics.duplicate()
        self._action_lock.release()
        return ret

    def get_next_job(self):
        """return next job that require externall processing"""
        if not self.is_run():
            return None
        ret = None
        self._action_lock.acquire()
        if len(self._complex_runners)>0:
            ret = self._complex_runners.pop()
            self._processed_runners.append(ret)
        self._action_lock.release()        
        if ret is None:
            return None        
        return ret
        
    def set_job_finished(self, job_id):
        """set job as finished"""
        if not self.is_run():
            return None
        self._action_lock.acquire()
        ret = None
        for runner in self._processed_runners:
            if job_id == runner.id:
                ret = runner                
                break
        self._processed_runners.remove(ret)
        self._finished_runners.append(ret)                
        self._action_lock.release()        

    def _pipeline_procesing(self):
        """function started in sepparate thread"""
        self._action_lock.acquire()
        while True:           
            if self._stop or self._pause:
                while True:
                    if self._stop:
                        # stop  after signall
                        self._is_run = False
                        self._action_lock.release()
                        return
                    if self._pause:
                        # pause after signall
                        self._action_lock.release()
                        time.sleep(1)                        
                        self._action_lock.acquire()
                    else:
                        break
            self._action_lock.release()
            state, runner = self._pipeline._run()
            self._action_lock.acquire()
            if state is ActionRunningState.finished:
                self._is_finished = True
                self._is_run = False
                self._action_lock.release()
                return
            if state is ActionRunningState.error:
                self._run_errs = runner
                self._is_run = False
                self._action_lock.release()
                return
            if runner is not None:
                self._complex_runners.append(runner)
                self._action_lock.release()
                statistics = self._pipeline._get_statistics()
                self._action_lock.acquire()
                self._statistics = statistics
            if state is ActionRunningState.wait:
                self._action_lock.release()
                time.sleep(1)                
                self._action_lock.acquire()
            while len(self._finished_runners)>0:
                runner = self._finished_runners.pop()
                self._action_lock.release()
                runner.action._after_run()
                statistics = self._pipeline._get_statistics()
                self._action_lock.acquire()
                self._statistics = statistics
        self._action_lock.release()
