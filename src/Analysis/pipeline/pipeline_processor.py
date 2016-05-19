"""Pipeline help function for internall using in tak JobScheduler only"""
import threading
import time
import subprocess
from .action_types import ActionRunningState, QueueType

class Pipelineprocessor():
    """
    Class for pipeline processing.
    
    This class contain pipeline action and
    process some job that is defined
    pipeline python script, pipeline validation
    and returning pipeline statiscics.
  
    Pipeline processing can be stated by run
    function and stoped by stop function. If pipeline
    is started, get_next_job function return next
    action for external processing, that can be 
    processed. After job processing is nessery call function 
    set_job_finished(). If not any job is available,
    get_next_job return None.
    
    All internall action is made in workers threads if
    action state is processed. Processed state is set
    in action code during _plan_action function and
    action is responsible for state locking. After settings 
    processed state is action assigned to one worker 
    thread, and in end of action processing is state
    set to finished. After this (in finished state) can't be 
    any update of action variables make. (Action output 
    for next action will be read from diferrent threads)
    
    !!! If run function is started, all operation with pipeline 
    is done in sepparate thread or workers threads. Variables
    runners arrays, _stop, pause and _statistics is
    protected by action_lock. Any access to pipeline can't
    be made directly from communication thread.
    """

    __workers__ = 4
    """Number of threads for processing internal jobs"""

    def __init__(self, pipeline):
        self._pipeline = pipeline
        """pipeline"""       
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
        self._action_lock = threading.Lock()
        """lock for _stop, _pause"""
        self._stop = False
        """signal to sepparate thread for stopping"""
        self._pause = False
        """signal to sepparate thread for pausing"""
        self._run_errs = []
        """errors during run"""
        
    class WorkerThread():
        _complex_runners=[]
        """Runners of independent actions that wait for external processing"""
        _processed_runners=[]
        """Runners of independent actions that are processing"""
        _finished_runners=[]
        """Runners of independent actions was processed"""
        _runners_lock = threading.Lock()
        """lock for runners"""
        def __init__(self):
            self._action = None
            """processed action"""
            self._stop = False
            """stop thread"""            
            self._action_lock = threading.Lock()
            """lock for action settings"""
            self._after_run = False
            """is processed after run externall action"""
            t = threading.Thread(target=self.run)
            t.daemon = True
            t.start()
            
        def add_action(self, action, after_run=False):
            """Add action if is empty, and return if is action added"""
            ret=False
            self._action_lock.acquire()
            if self._action is None:
                self._after_run=after_run
                self._action = action
                ret = True
            self._action_lock.release()            
            return ret            
        
        def is_empty(self):
            """Add action if is empty, and return if is action added"""
            ret=False
            self._action_lock.acquire()
            if self._action is None:
                ret = True
            self._action_lock.release()
            return ret            
        
        def run(self):
            """worker thread"""
            while True:
                is_action = False
                while not is_action:                
                    self._action_lock.acquire()
                    if self._stop:
                        self._action_lock.release()
                        return
                    if self._action is not None:
                        is_action = True
                    self._action_lock.release()
                    if not  is_action:
                        time.sleep(0.1)
                if self._after_run:
                    self._action._after_update()
                else:
                    runner = self._action._update()
                    if runner is not None:
                        if self._action is QueueType.internal:
                            process = subprocess.Popen(runner.command)
                            self._action._after_update()
                        else:
                            self._runners_lock.acquire()
                            self._complex_runners.append(runner)
                            self._runners_lock.release()
                    else:
                        self._action._after_update()
                self._action_lock.acquire()
                self._action = None
                self._action_lock.release()
        
        def stop(self):
            self._action_lock.acquire()
            self._stop = True
            self._action_lock.release()
        
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
        return self._pipeline._get_statistics()

    def get_next_job(self):
        """return next job that require externall processing"""
        if not self.is_run():
            return None
        ret = None
        self.WorkerThread._runners_lock.acquire()
        if len(self.WorkerThread._complex_runners)>0:
            ret = self.WorkerThread._complex_runners.pop()
            self.WorkerThread._processed_runners.append(ret)
        self.WorkerThread._runners_lock.release()        
        if ret is None:
            return None        
        return ret
        
    def set_job_finished(self, job_id):
        """set job as finished"""
        if not self.is_run():
            return None
        self.WorkerThread._runners_lock.acquire()
        ret = None
        for runner in self.WorkerThread._processed_runners:
            if job_id == runner.id:
                ret = runner                
                break
        self.WorkerThread._processed_runners.remove(ret)
        self.WorkerThread._finished_runners.append(ret)                
        self.WorkerThread._runners_lock.release()

    def _pipeline_procesing(self):
        """function started in sepparate thread"""
        workers=[]
        """ threads for processing internal jobs"""
        wait_actions = []
        """action that can be processed"""
        
        for i in range(0, self.__workers__):
            workers.append(self.WorkerThread())
        while True:           
            self._action_lock.acquire()
            if self._stop or self._pause:
                while True:
                    if self._stop:
                        # stop  after signall
                        for worker in workers:
                            if worker.is_empty():
                                worker.stop()
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
            state = ActionRunningState.repeat
            # get all available actions
            while state is ActionRunningState.repeat:
                state, action = self._pipeline. _plan_action()
                i +=1
                if action is not None:
                    wait_actions.append(action)
            sorted(wait_actions, key=lambda item: item._get_priority())
            # finished external tasks
            for worker in workers:
                self.WorkerThread._runners_lock.acquire()
                if len(self.WorkerThread._finished_runners)==0:
                    self.WorkerThread._runners_lock.release()
                    break
                self.WorkerThread._runners_lock.release()
                if worker.is_empty():  
                    self.WorkerThread._runners_lock.acquire()
                    runner = self.WorkerThread._finished_runners.pop()
                    self.WorkerThread._runners_lock.release()   
                    worker.add_action(runner.action, True)
            # try add action to workers
            if len(wait_actions)==0:
                time.sleep(0.1)
            try:
                action = wait_actions.pop() 
                for worker in workers:
                    if worker. add_action(action):
                        action = wait_actions.pop()
                wait_actions.append(action)
            except IndexError:
                # empty queue
                pass
            if state is ActionRunningState.finished and \
                len(self.WorkerThread._complex_runners) == 0 and \
                len(self.WorkerThread._processed_runners) == 0 and \
                len(self.WorkerThread._finished_runners) == 0 and \
                len(wait_actions) == 0:
                #wait for  finishing worker threads
                for worker in workers:
                    if worker.is_empty():
                        worker.stop()
                self._action_lock.acquire()                
                self._is_finished = True
                self._is_run = False
                self._action_lock.release()
                return   
            if state is ActionRunningState.error:
                for worker in workers:
                    if worker.is_empty():
                        worker.stop() 
                self._run_errs = runner
                self._action_lock.acquire()
                self._is_run = False
                self._action_lock.release()
                return
