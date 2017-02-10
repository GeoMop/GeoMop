# -*- coding: utf-8 -*-
"""
JobPanel data reloader
@author: Jan Gabriel
@contact: jan.gabriel@tul.cz
"""
import os
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

        - call stop_all or pause_all function and wait till run_jobs, delete_jobs and start_jobs array is not empty


     JB, TODO: Describe better data structures. What are individual states/queues exactly?
    """
    def __init__(self, data_app):        
        self._workers = dict()
        self._data_app = data_app
        self.current_job = None
        """
        current job id
        What is current_job?
        """
        self.start_jobs = []
        """array of job ids, that will be started"""
        self.resume_jobs = []
        """array of jobs ids, that will be resume"""
        self.stop_jobs = []
        """array of jobs ids, that will be stopped"""
        self.delete_jobs = []
        """array of jobs ids, that will be stopped"""
        self.run_jobs = []
        """array of running jobs ids"""
        self.terminate_jobs = []
        """array of jobs ids, that will be destroyed (try restart job and delete all processes and data)"""
        self.state_change_jobs = []
        """array of jobs ids, that have changed state"""
        self.results_change_jobs = []
        """array of jobs ids, that have changed results"""
        self.jobs_change_jobs = []
        """array of jobs ids, that have changed jobs state"""
        self.jobs_deleted = {}
        """
        Dictionary of jobs ids=>None (ids=>error), that was deleted data.
        If job was not deleted, in dictionary value is error text 
        """
        self.logs_change_jobs=[]
        """array of jobs ids, that have changed jobs logs"""
        self.__cancel_jobs = []
        """private array of jobs ids, that wait for cancelling"""
        
    def poll(self):
        """
        This function plans and makes all the needed actions in the main thread.
        Function should be called periodically from the UI.
        """
        bussy = True
        if not self._terminate() and not self._stop():
            if not self._resume_first():
                if not self._delete_first():
                    if not self._start_first():
                        bussy = False
        if not bussy:
            bussy = bussy or self._check_resumed()
        if not bussy:
            bussy = bussy or self._check_deleted()
        if not bussy:
            bussy = bussy or self._check_started()

        self._refresh_queues()
        if not bussy:
            self._check_cancelled()

    def _refresh_queues(self):
        """start first job in queue and return True else return False"""       
        for  key in self.run_jobs:
            if key in self._workers:
                worker = self._workers[key]
                is_current = self.current_job is not None and self.current_job == key
                state, error, jobs_downloaded, results_downloaded , logs_downloaded = worker.get_last_results(is_current)
                if state is not None or error is not None:
                    self._set_state(key, state, error)
                    self.state_change_jobs.append(key)
                if jobs_downloaded:
                    self.jobs_change_jobs.append(key)
                if results_downloaded:
                    self.results_change_jobs.append(key)
                if logs_downloaded:
                    self.logs_change_jobs.append(key)
                if state is not None and state.status == TaskStatus.ready and \
                    not  worker.is_cancelling():   
                    worker.finish()
                    self.__cancel_jobs.append(key) 
            
    def _start_first(self):
        """start first job in queue and return True else return False"""
        for  key in  self.start_jobs:
            if not key in self._workers:
                conf_builder = ConfigBuilder(self._data_app)
                app_conf = conf_builder.build(key)
                ConfigBuilder.gain_login(app_conf)                
                com = Communicator(app_conf)
                worker = ComWorker(key, com)
                self._workers[key] = worker
                worker.start_mj()
                return True
        return False

    def _resume_first(self):
        """resume first job in queue and return True else return False"""
        for  key in  self.resume_jobs:
            if not key in self._workers:
                self.__resume_mj(key)
                self._workers[key].resume()
                return True
        return False
    
    def __is_mj_initialized(self, key):
        """return if was mj started (dconfig directory was initialized)"""
        mj = self._data_app.multijobs[key]
        mj_name = mj.preset.name
        an_name = mj.preset.analysis
        directory = inst.Installation.get_config_dir_static(mj_name, an_name)
        path = comconf.CommunicatorConfigService.get_file_path(
            directory, comconf.CommType.app.value)
        return  os.path.isfile(path)

    def __resume_mj(self, key):
        mj = self._data_app.multijobs[key]
        mj_name = mj.preset.name
        an_name = mj.preset.analysis
        com_conf = comconf.CommunicatorConfig(mj_name)
        directory = inst.Installation.get_config_dir_static(mj_name, an_name)
        path = comconf.CommunicatorConfigService.get_file_path(
            directory, comconf.CommType.app.value)        
        with open(path, "r") as json_file:
            comconf.CommunicatorConfigService.load_file(json_file, com_conf)
            ConfigBuilder.gain_login(com_conf)
        com = Communicator(com_conf)
        worker = ComWorker(key, com)
        self._workers[key] = worker

                
    def _delete_first(self):
        """delete first job in queue and return True else return False"""
        for  key in self.delete_jobs:
            if not key in self._workers:
                if not self.__is_mj_initialized(key):
                    self.jobs_deleted[key] = None
                    self.delete_jobs.remove(key)
                else:
                    self.__resume_mj(key)
                    self._workers[key].delete()
                return True
        return False

    def _stop(self):
        """
        stop all job in queue and return True else return False
        """
        res = False
        while len(self.stop_jobs)>0:
            key = self.stop_jobs.pop()
            if key in self._workers:
                worker = self._workers[key] 
                if not worker.is_cancelling():                    
                    worker.stop()
                    self.__cancel_jobs.append(key) 
                    res = True
            else:
                ComWorker.get_loger().error("MultiJob {0} can't be stopped, run record is not found")
                return
        return res

    def _terminate(self):
        """
        terminate all jobs in queue and return True else return False

        JB, Question: What is difference between terminate and stop?

        """
        res = False
        while len(self.terminate_jobs)>0:
            key = self.terminate_jobs.pop()
            if key in self._workers:
                worker = self._workers[key] 
                if not worker.is_cancelling():                    
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
                if worker.is_interupted() or worker.is_error():
                    mj = self._data_app.multijobs[key]
                    mj.error = worker.get_error()
                    if worker.is_interupted():
                        mj.get_state().set_status(TaskStatus.interupted)
                        self.run_jobs.append(key)
                    else:
                        mj.get_state().set_status(TaskStatus.error)
                        del self._workers[key]                    
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
            self.resume_jobs.remove(key)

    def _check_deleted(self):
        """
        check all job in deleted queue, move deleted to run 
        queue and send get_state message. Update job states.
        """
        delete_key = []
        for  key in  self.delete_jobs:
            if key in self._workers:
                worker = self._workers[key]
                if worker.is_cancelled():
                    if (worker.is_interupted() or worker.is_error()) and \
                        not worker.is_deleting():
                        error = worker.get_error()
                        if worker.is_interupted():
                            error = "Can't delete remote data from MultiJob (no response)" 
                        del self._workers[key]
                        self.jobs_deleted[key] = error
                        delete_key.append(key)
                    elif worker.is_deleted():
                        error = None
                        if worker.is_error():
                            error = worker.get_error()
                        del self._workers[key]
                        self.jobs_deleted[key] = error
                        delete_key.append(key)
            else:
                ComWorker.get_loger().error("MultiJob {0} can't be deleted, run record is not found")
                delete_key.append(key)
                break
        for key in delete_key:
            self.delete_jobs.remove(key)


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
                elif worker.is_error():
                    mj = self._data_app.multijobs[key]
                    mj.get_state().set_status(TaskStatus.error)
                    mj.error = worker.get_error()
                    self.state_change_jobs.append(key)
                    delete_key.append(key)
                    del self._workers[key]
                else:
                    state, qued_time = worker.get_start_state()
                    mj = self._data_app.multijobs[key]
                    if mj.get_state().get_status() != state:
                        mj.get_state().set_status(state)
                        mj.state.qued_time = qued_time
                        self.state_change_jobs.append(key)
            else:
                ComWorker.get_loger().error("MultiJob {0} can't be started, run record is not found")
                delete_key.append(key)
                break
        for key in delete_key:
            self.start_jobs.remove(key)

    def _check_cancelled(self):
        """
        if is mj in cancelled queue and is cancelled, delete worker and remove mj from queue
        """
        delete_key = []
        for  key in self.__cancel_jobs:
            if key in self._workers:
                worker = self._workers[key]
                if worker.is_cancelled():
                    delete_key.append(key)
                    self._refresh_queues()
            else:
                ComWorker.get_loger().error("MultiJob {0} can't be stopped, run record is not found")
                delete_key.append(key)
                break
        for key in delete_key:
            self.__cancel_jobs.remove(key)
            self.run_jobs.remove(key)            
            del self._workers[key]
        
    def _set_state(self, key, state, error):
        """
        Set state for set job
        """
        mj = self._data_app.multijobs[key]
        if state is not None:
            mj.state.update(state)
            mj.error = error
        else:     
            if error is not None:
                mj.error = error

    def pause_all(self):
        """Pause all running and starting jobs (use when app is closing)."""
        for  key in  self.run_jobs:
            if key in self._workers:
                worker = self._workers[key] 
                if not worker.is_cancelling():                    
                    worker.pause()
                    self.__cancel_jobs.append(key) 
            else:
                ComWorker.get_loger().error("MultiJob {0} can't be paused, run record is not found")
        
    def stop_all(self):
        """stop all running and starting jobs"""
        for  key in  self.run_jobs:
            if key in self._workers:
                worker = self._workers[key] 
                if not worker.is_cancelling():                    
                    worker.stop()
                    self.__cancel_jobs.append(key) 
            else:
                ComWorker.get_loger().error("MultiJob {0} can't be stopped, run record is not found")
