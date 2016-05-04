"""Pipeline help function for internall using in tak JobScheduler only"""
import threading
import time
from .action_types import ActionType, ActionStateType

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
        
    def duplicate(self):
        ret = PipelineStatistics()
        ret.known_jobs = self.known_jobs
        ret.estimated_jobs = self.estimated_jobs
        ret.finished_jobs = self.finished_jobs
        ret.running_jobs = self.running_jobs
        return ret

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
        """lock for action arrays, _stop and _statistics variables"""
        self._stop = False
        """signal to sepparate thread for stopping"""
        self._run_errs = []
        """errors during run"""

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
            self._sorte_jobs()
            self._set_statistics()
        except Exception as err:
            self._errs.append("Exception during validation: " + str(err))
        self._is_validate = True        
        return self._errs

    def is_run(self):
        """return if if pipeline processor is started"""
        self._action_lock.acquire()
        res = self._stop = True
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
        self._prestart_preparration()
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
        if len(self._wait_actions)>0:
            for i in range(0, len(self._wait_actions)):
                if self._wait_actions[i]._type == ActionType.complex:
                    i_action = i
                    break                        
            if i_action is not None:
                ret = self._wait_actions.pop(i_action)
                self._processed_actions.append(ret)
                self._statistics.known_jobs -= 1
                self._statistics.estimated_jobs -= 1
                self._processed_actions += 1
        self._action_lock.release()
        if ret is None:
            return None
        return ret._run()
        
    def set_job_finished(self, job_id):
        """set job as finished"""
        if not self.is_run():
            return None
        self._action_lock.acquire()
        ret = None
        for action in self._processed_actions:
            if job_id == action._id:
                ret = action
                break
        ret._after_run()        
        # action is left in processed action array, end is repear only statistics
        # action will be move in right array in separate thread
        self._processed_actions -= 1
        self._self._finished_actions += 1
        self._action_lock.release()

    def _set_statistics(self):
        self._action_lock.acquire()
        self._statistics = PipelineStatistics()
        for action in self._dependent_actions:
            if action._type == ActionType.complex:
                self._statistics.known_jobs += 1
                self._statistics.estimated_jobs += 1
            self._statistics.estimated_jobs += action._pending_actions
        for action in self._wait_actions:
            if action._type == ActionType.complex:
                self._statistics.known_jobs += 1
                self._statistics.estimated_jobs += 1
            self._statistics.estimated_jobs += action._pending_actions
        for action in self._processed_actions:
            if action._type == ActionType.complex:
                self._statistics.known_jobs += 1
            self._statistics.estimated_jobs += action._pending_actions
        for action in self._finished_actions:
            if action._type == ActionType.complex:
                self._statistics.finished_jobs += 1            
        self._action_lock.release()
        
    def _sorte_jobs(self):
        """init or reinit action arrais"""
        self._action_lock.acquire()
        actions = self._pipeline._get_child_list()
        self._finished_actions = []
        self._processed_actions = []
        rest = []
        self._dependent_actions = []
        self._wait_actions = []
        for action in actions:
            if action._state is ActionStateType.finished:
                self._finished_actions.append(action)
            elif action._state is ActionStateType.process:
                self._processed_actions.append(action)
            else:
                rest.append(action)
        for action in rest:
            dependent = False
            for input in action._inputs:
                if input not in self._finished_actions:
                    self._dependent_actions.append(action)
                    dependent = True
                    break
            if not dependent:
                self._wait_actions.append(action)
        self._action_lock.release()
       
    def _pipeline_procesing(self):
        """function started in sepparate thread"""
        self._action_lock.acquire()
        while (len(self._processed_actions)+len(self._dependent_actions)+ \
            len(self._wait_actions))>0:
            self._action_lock.release()
            while True:
                self._action_lock.acquire()
                if self._stop:
                    # stop  after signall
                    self._is_run = False
                    self._action_lock.release()
                    return
                if len(self._processed_actions) == 0 and \
                    len(self._dependent_actions)>0 and \
                    len(self._wait_actions) == 0:
                    # stop after err
                    self._run_errs.append("Some dependent action rest in queue.")
                    self._is_run = False
                    self._action_lock.release()                    
                    return
                # proces simple actions
                i_action = None
                for i in range(0, len(self._wait_actions)):
                    if self._wait_actions[i]._type == ActionType.simple:
                        i_action = i
                        break                        
                if i_action is None:
                    self._action_lock.release()
                    break
                action = self._wait_actions.pop(i_action)
                self._action_lock.release()
                action._run()
            # wait for new simple actions
            is_simple = False 
            while not is_simple:
                self._sorte_jobs()
                self._set_statistics()
                self._action_lock.acquire()
                if len(self._processed_actions)==0:
                    is_simple = True
                else:
                    for i in range(0, len(self._wait_actions)):
                        if self._wait_actions[i]._type == ActionType.simple:
                            is_simple = True
                            break                        
                self._action_lock.release()
                if not is_simple:
                    time.sleep(1)        
        self._is_finished = True
        self._is_run = False
        self._action_lock.release()
