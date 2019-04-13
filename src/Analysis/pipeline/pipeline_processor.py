"""Pipeline help function for internall using in tak JobPanel only"""
import threading
import time
import subprocess
import logging
import os
import shutil
from .action_types import ActionRunningState, QueueType
from .identical_list import  IdenticalList

logger = logging.getLogger("Analysis")

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
    For logging is used standart python logging, that is thread-save
    """

    __workers__ = 4
    """Number of threads for processing internal jobs"""

    def __init__(self, pipeline, log_path=None, log_level=logging.WARNING, save_path="./backup", identical_list=None):
        self._pipeline = pipeline
        """pipeline"""       
        self._is_validate = False
        """
        Validation is processed by calling validate function. After validation
        is errs variable set. If is some records in this variable, sepparated
        thread can't be started and run function raise exception. If run
        function is call without validate function, validation is make in run
        internaly.
        
        :param Pipeline pipeline: Loaded pipeline
        :param string log_path: Path for loging. Log is needed only for action
            processing, and for action planning should be None
        :param string log_level: Loging level
        :param string save_path: Path for result backup file, where is place
            file with last run results and is save files ready actions
        :param string identical_list: path to file with list of equol action for 
            establishing connection. File identical_list is needed only for action
            processing, and for action planning should be None. Equal list is
            created in client site by :class:`client_pipeline.identical_list_creator.ELCreator`.
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
        self._save_path = save_path
        """path for result saving (read-only)"""
        if log_path is not None:
            self.__set_loger(log_path,  log_level)
        self._save_path = save_path
        self.WorkerThread._save_path = save_path
        self._establish_processing(identical_list)
        
    class WorkerThread():
        _complex_runners=[]
        """Runners of independent actions that wait for external processing"""
        _processed_runners=[]
        """Runners of independent actions that are processing"""
        _finished_runners=[]
        """Runners of independent actions was processed"""
        _runners_lock = threading.Lock()
        """lock for runners"""
        _save_path = None
        """path for result saving (read-only)"""
        def __init__(self):
            self._action = None
            """processed action"""
            self._stop = False
            """stop thread"""            
            self._action_lock = threading.Lock()
            """lock for action settings"""
            self._after_run = False
            """is processed after run externall action"""
            self._error = None
            """Processing error"""
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
                    self._action._after_update(self._save_path)
                    logger.info("External action {0} processing is ended".format(
                        self._action. _get_instance_name()))
                else:
                    runner = self._action._update()
                    if runner is not None:
                        if self._action is QueueType.internal:
                            logger.info("Internal action {0} processing is began".format(
                                self._action. _get_instance_name()))
                            process = subprocess.Popen(runner.command, stderr=subprocess.PIPE, cwd=runner.work_dir)
                            return_code = process.poll()
                            if return_code is not None:
                                out = process.stderr.read().decode(errors="replace")
                                err = "Can not start action {0}(return code:{1} ,stderr:{2}".format(
                                    self._action. _get_instance_name(), str(return_code), out)
                                logger.error(err)
                                self._action_lock.acquire()
                                self._error = err
                                self._action_lock.release()
                            else:
                                self._action._after_update(self._save_path)
                                logger.info("Internal action {0} processing is ended".format(
                                    self._action. _get_instance_name()))
                        else:
                            logger.info("External action {0} processing is began".format(
                                self._action. _get_instance_name()))
                            self._runners_lock.acquire()
                            self._complex_runners.append(runner)
                            self._runners_lock.release()
                    else:
                        self._action._after_update(self._save_path)
                        logger.info("Short action {0} processing is finished".format(
                            self._action. _get_instance_name()))
                self._action_lock.acquire()
                self._action = None
                self._action_lock.release()

        def stop(self):
            self._action_lock.acquire()
            self._stop = True
            self._action_lock.release()
            
        def get_error(self):
            self._action_lock.acquire()
            err = self._error
            self._action_lock.release()
            return err
        
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
            logger.info("Analysis processing is started")
            return
        if not self._is_validate:
            self.validate()
        if len(self._errs) > 0:
            logger.error("Analysis validation return errors:\n    {0}".format(
                '\n    '.join(self._errs)))
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
        
    def _establish_processing(self, identical_list):
        """
        this function follow up last processing, mark processed
        actions that haven't changes and have result, load their
        result from backup and set their as finished.
        """
        # prepare store and restor folders
        if not os.path.isdir(self._save_path):
            try:
                os.makedirs(self._save_path)
            except Exception as err:
                error = "Can't make save path {0} ({1})".format(self._save_path, str(err))
                logger.error(error)
                raise Exception(error)
        store_path = os.path.join(self._save_path, "store")
        restore_path = os.path.join(self._save_path, "restore")
        if not os.path.isdir(store_path):            
            try:
                os.makedirs(store_path)
            except Exception as err:
                error = "Can't make store path {0} ({1})".format(store_path, str(err))
                logger.error(error)
                raise Exception(error)
            try:
                if os.path.isdir(restore_path):
                    shutil.rmtree(restore_path, ignore_errors=True)
                os.makedirs(restore_path)
            except Exception as err:
                error = "Can't make restore path {0} ({1})".format(restore_path, str(err))
                logger.error(error)
                raise Exception(error)
        else:
            try:
                if os.path.isdir(restore_path):
                    shutil.rmtree(restore_path, ignore_errors=True)
                os.rename(store_path,restore_path)
                os.makedirs(store_path)
            except Exception as err:
                error = "Can't copy store path {0} to restore path {1} ({2})".format(
                    store_path, restore_path, str(err))
                logger.error(error)
                raise Exception(error)
        il = None
        if identical_list is not None:
            il = IdenticalList()
            il.load(identical_list)
            self._pipeline._set_restore_id(il)

        # rename output files
        output_tmp_dir = "output_tmp"
        shutil.rmtree(output_tmp_dir, ignore_errors=True)
        os.makedirs(output_tmp_dir)
        for entry in os.listdir("."):
            if os.path.isdir(entry) and entry.startswith("action_"):
                shutil.move(entry, os.path.join(output_tmp_dir, entry[7:]))
        if il is not None:
            inverse_il = {v: k for k, v in il._instance_dict.items()}
            for entry in os.listdir(output_tmp_dir):
                tmp_output = os.path.join(output_tmp_dir, entry, "output")
                if os.path.isdir(tmp_output):
                    s = entry.split(sep="_", maxsplit=1)
                    old_id = s[0]
                    if len(s) == 2:
                        suffix = "_" + s[1]
                    else:
                        suffix = ""
                    if old_id in inverse_il:
                        new_id = inverse_il[old_id]
                        action_dir = "action_" + new_id + suffix
                        os.makedirs(action_dir)
                        shutil.move(tmp_output, os.path.join(action_dir, "output"))
        shutil.rmtree(output_tmp_dir, ignore_errors=True)

    def __set_loger(self,  path,  level):
        """set logger"""        
        if not os.path.isdir(path):
            try:
                os.makedirs(path)
            except:
                return
        log_file = os.path.join(path, "analysis.log")            
        logger = logging.getLogger("Analysis")
        logger.setLevel(level)
        fh = logging.FileHandler(log_file)
        fh.setLevel(level)

        formatter = logging.Formatter(
            '%(asctime)s %(levelname)s %(message)s')

        fh.setFormatter(formatter)
        logger.addHandler(fh)    

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
                state, action = self._pipeline. _plan_action(self._save_path)
                if action is not None and state is not ActionRunningState.finished:
                    wait_actions.append(action)
            wait_actions = sorted(wait_actions, key=lambda item: item._get_priority())
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
                # TODO: asi se zapisuji věci do souborů, zjistit proč
                time.sleep(0.1)
                self._action_lock.acquire()
                self._is_finished = True
                self._is_run = False
                self._action_lock.release()
                return
            if state is ActionRunningState.error:
                logger.error("Analysis processing return errors:\n    {0}".format(
                    '\n    '.join(runner)))
            for worker in workers:
                err = worker.get_error()
                if err is not None:
                    # error is logged in worker
                    runner = [err]
                    state = ActionRunningState.error
                    break 
            if state is ActionRunningState.error:
                for worker in workers:
                    if worker.is_empty():
                        worker.stop() 
                self._run_errs = runner
                self._action_lock.acquire()
                self._is_run = False
                self._action_lock.release()
                return
