# -*- coding: utf-8 -*-
"""
JobScheduler data reloader
@author: Jan Gabriel
@contact: jan.gabriel@tul.cz
"""
from communication import Communicator
import data.communicator_conf as comconf
import communication.installation as inst
from ui.data.config_builder import ConfigBuilder
from ui.com_worker import ComWorker
from data.states import TaskStatus


class ComManager:
    """
    Usage:
    
        - set application data to constructor
        - add job id (key) to array (start_jobs,stop_jobs,resume_jobs,terminate_jobs)
        - if current job is changed, set it
        - each 0.5s call check function in main thread, after check returning should be done:    
        
                - from arrays state_change_jobs,results_change_jobs,jobs_change_jobs pull
                   jobs, and fix graphic presentation
                - if application is stopping, check run_jobs and start_jobs arrays (in this case,
                  check function can be call with higher frequency)

        - call stop_all or pause_all function and wait till run_jobs and start_jobs array is not empty
    """
    def __init__(self, data_app):        
        self._workers = dict()
        self._data_app = data_app
        self.current_job = None
        """current job id"""
        self.start_jobs = []
        """array of job ids, that will be started"""
        self.resume_jobs = []
        """array of jobs ids, that will be resume"""
        self.stop_jobs = []
        """array of jobs ids, that will be stopped"""
        self.run_jobs = []
        """array of running jobs ids"""
        self.terminate_jobs = []
        """array of jobs ids, that will be destroyed (try restart job and delete all processes and data)"""
        self.state_change_jobs=[]
        """array of jobs ids, that have changed state"""
        self.results_change_jobs=[]
        """array of jobs ids, that have changed results"""
        self.jobs_change_jobs=[]
        """array of jobs ids, that have changed jobs state"""
        self.logs_change_jobs=[]
        """array of jobs ids, that have changed jobs logs"""
        self.__cancel_jobs = []
        """private array of jobs ids, that wait for canceling"""
        
    def poll(self):
        """
        This function plans and makes all the needed actions in the main thread.
        Function should be called periodically from the UI.
        """
        bussy = True
        if not self._terminate() and not self._stop():
            if not self._resume_first():
                if not self._start_first():
                    bussy = False
        if not bussy:
            bussy = bussy or self._check_resumed()
        if not bussy:
            bussy = bussy or self._check_started()
        for  key in self.run_jobs:
            if key in self._workers:
                worker = self._workers[key]
                state, error, jobs_downloaded, results_downloaded , logs_downloaded = worker.get_last_results()
                if state is not None or error is not None:
                    self._set_state(key, state, error)
                    self.state_change_jobs.append(key)
                if jobs_downloaded is not None:
                    self.jobs_change_jobs.append(key)
                if results_downloaded is not None:
                    self.results_change_jobs.append(key)
                if logs_downloaded is not None:
                    self.logs_change_jobs.append(key)
                if state is not None and state.status == TaskStatus.finished:   
                    worker.finish()
                    self.__cancel_jobs.append(key) 
        if not bussy:
            self._check_canceled()
            
    def _start_first(self):
        """start first job in queue and return True else return False"""
        for  key in  self.start_jobs:
            if not key in self._workers:
                mj = self.data.multijobs[key]
                analysis = self._reload_project(mj)
                conf_builder = ConfigBuilder(self.data)
                app_conf = conf_builder.build(key, analysis)
                com = Communicator(app_conf)
                worker = ComWorker(key, com)
                self._workers[worker.key] = worker
                worker.start()
                return True
        return False

    def _resume_first(self):
        """resume first job in queue and return True else return False"""
        for  key in  self.resume_jobs:
            if not key in self._workers:
                mj = self.data.multijobs[key]
                mj_name = mj.preset.name
                com_conf = comconf.CommunicatorConfig(mj_name)
                directory = inst.Installation.get_config_dir_static(mj_name)
                path = comconf.CommunicatorConfigService.get_file_path(
                    directory, comconf.CommType.delegator.value)
                with open(path, "r") as json_file:
                    comconf.CommunicatorConfigService.load_file(json_file, com_conf)                    
                com = Communicator(com_conf)
                worker = ComWorker(key, com)
                self._workers[worker.key] = worker
                worker.resume()
                return True
        return False

    def _stop(self):
        """stop all job in queue and return True else return False"""
        res = False
        while len(self.stop_jobs)>0:
            key = self.stop_jobs.pop()
            if key in self._workers:
                worker = self._workers[key] 
                if not worker.canceling():                    
                    worker.stop()
                    self.__cancel_jobs.append(key) 
                    res = True
            else:
                ComWorker.get_loger().error("MultiJob {0} can't be stopped, run record is not found")
                return
        return res

    def _terminate(self):
        """terminate all jobs in queue and return True else return False"""
        res = False
        while len(self.terminate_jobs)>0:
            key = self.terminate_jobs.pop()
            if key in self._workers:
                worker = self._workers[key] 
                if not worker.canceling():                    
                    worker.terminate()
                    self.__cancel_jobs.append(key) 
                    res = True
            else:
                ComWorker.get_loger().error("MultiJob {0} can't be terminate, run record is not found")
        return res

    def _check_resumed(self):
        """
        check all job in resume queue, move resumed to run 
        queue and send get_state message. Update job states.
        """
        delete_key = []
        for  key in  self.resume_jobs:
            if key in self._workers:
                worker = self._workers[key]
                if worker.is_interupted(self) or worker.is_error(self):
                    mj = self.data.multijobs[key]
                    mj.error = worker.get_error()
                    if worker.is_interupted(self):
                        mj.get_state().set_status(TaskStatus.interupted)
                        self.run_jobs.append(key)
                    else:
                        mj.get_state().set_status(TaskStatus.error)
                        self._workers.remove(key)                    
                    self.state_change_jobs.append(key)
                    delete_key.append(key)
                elif worker.is_started():
                    self.run_jobs.append(key)
                    worker.init_update()
                    delete_key.append(key)                
            else:
                ComWorker.get_loger().error("MultiJob {0} can't be resume, run record is not found")
                delete_key.append(key)
                break
        for key in delete_key:
            self.start_jobs.remove(key)

    def _check_started(self):
        """
        check all job in resume queue, move resumed to run 
        queue and send get_state message. Update job states.
        """
        delete_key = []
        for  key in  self.start_jobs:
            if key in self._workers:
                worker = self._workers[key]
                if worker.is_started():
                    self.run_jobs.append(key)
                    worker.init_update()
                    delete_key.append(key)
                elif worker.is_error(self):
                    mj = self.data.multijobs[key]
                    mj.get_state().set_status(TaskStatus.error)
                    mj.error = worker.get_error()
                    self.state_change_jobs.append(key)
                    delete_key.append(key)
                    self._workers.remove(key)
                else:
                    state = worker.get_start_state()
                    mj = self.data.multijobs[key]
                    if mj.get_state().get_status() != state:
                        mj.get_state().set_status(state)
                        self.state_change_jobs.append(key)
            else:
                ComWorker.get_loger().error("MultiJob {0} can't be started, run record is not found")
                delete_key.append(key)
                break
        for key in delete_key:
            self.start_jobs.remove(key)

    def _check_canceled(self):
        """
        if is mj in canceled queue and is canceled, delete worker and remove mj from queue
        """
        delete_key = []
        for  key in self.__cancel_jobs:
            if key in self._workers:
                worker = self._workers[key]
                if worker.is_cancelled():
                    status, error = worker.get_canceling_state()
                    delete_key.append(key)
                    mj = self.data.multijobs[key]
                    mj.get_state().set_status(status)
                    mj.error = error
            else:
                ComWorker.get_loger().error("MultiJob {0} can't be stopped, run record is not found")
                delete_key.append(key)
                break
        for key in delete_key:
            self.__cancel_jobs.remove(key)
            self.run_jobs.remove(key)
            self._workers.remove(key)
        
    def _set_state(self, key, state, error):
        """
        Set state for set job
        """
        mj = self.data.multijobs[key]
        if state is not None:
            mj.update(state)
            mj.error = error
        else:     
            if error is not None:
                mj.error = error

    def pause_all(self):
        """Pause all running and starting jobs (use when app is closing)."""
        for  key in  self.run_jobs:
            if key in self._workers:
                worker = self._workers[key] 
                if not worker.canceling():                    
                    worker.pase()
                    self.__cancel_jobs.append(key) 
            else:
                ComWorker.get_loger().error("MultiJob {0} can't be paused, run record is not found")
        
    def stop_all(self):
        """stop all running and starting jobs"""
        for  key in  self.run_jobs:
            if key in self._workers:
                worker = self._workers[key] 
                if not worker.canceling():                    
                    worker.stop()
                    self.__cancel_jobs.append(key) 
            else:
                ComWorker.get_loger().error("MultiJob {0} can't be stopped, run record is not found")
