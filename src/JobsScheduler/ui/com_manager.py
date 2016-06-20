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
        
    def check(self):
        """
        This function plan and make all needed action in main thread.
        Call this function in some period
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
        if not bussy:
            bussy = bussy or self._check_stopped()
        if not bussy:
            bussy = bussy or self._check_terminated()
        if  bussy:
            return
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
        for  key in  self.stop_jobs:
            if key in self._workers:
                worker = self._workers[key] 
                if not worker.is_stopping() and not worker.is_stopped():
                    worker.stop()
                    res = True
            else:
                ComWorker.get_loger().error("MultiJob {0} can't be stopped, run record is not found")
                self.stop_jobs.remove(key)
                return
        return res

    def _terminate(self):
        """terminate all jobs in queue and return True else return False"""
        res = False
        for  key in  self.terminate_jobs:
            if key in self._workers:
                worker = self._workers[key] 
                if not worker.is_terminating() and not worker.is_terminated():
                    worker.terminate()
                    res = True
            else:
                ComWorker.get_loger().error("MultiJob {0} can't be terminate, run record is not found")
                self.stop_jobs.remove(key)
                return
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
                if worker.is_started():
                    self.run_jobs.append(key)
                    worker.init_update()
                    delete_key.append(key)
                elif worker.is_iterupted(self) or worker.is_error(self):
                    mj = self.data.multijobs[key]
                    if worker.is_iterupted(self):
                        mj.get_state().set_status(TaskStatus.interupted)
                    else:
                        mj.get_state().set_status(TaskStatus.error)
                    self.state_change_jobs.append(key)
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
                elif worker.is_iterupted(self) or worker.is_error(self):
                    mj = self.data.multijobs[key]
                    if worker.is_iterupted(self):
                        mj.get_state().set_status(TaskStatus.interupted)
                    else:
                        mj.get_state().set_status(TaskStatus.error)
                    self.state_change_jobs.append(key)
                    delete_key.append(key)
            else:
                ComWorker.get_loger().error("MultiJob {0} can't be started, run record is not found")
                delete_key.append(key)
                break
        for key in delete_key:
            self.start_jobs.remove(key)


    def _check_stopped(self):
        """
        check all job in resume queue, move resumed to run 
        queue and send get_state message. Update job states.
        """

    def _check_terminated(self):
        """
        check all job in resume queue, move resumed to run 
        queue and send get_state message. Update job states.
        """
    def _set_state(self, key, state, error):
        """
        Set state for set job
        """

    def pause_all(self):
        """resume all running and starting jobs"""
        
    def stop_all(self):
        """stop all running and starting jobs"""
        
    # next funcion will be delete after refactoring

    def create_worker(self, key, com):        
        worker = ComWorker(key=key, com=com, res_queue=self.res_queue)
        self._workers[worker.key] = worker

    def install(self, key, com):
        worker = ComWorker(key=key, com=com, res_queue=self.res_queue)
        req_install = ReqData(key=key, com_type=ComType.install)
        req_results = ReqData(key=key, com_type=ComType.results)
        worker.req_queue.put(req_install)
        worker.req_queue.put(req_results)
        self._workers[worker.key] = worker

    def pause(self, key):
        if key in self._workers:
            worker = self._workers[key]        
            worker.is_ready.clear()
            req = ReqData(key=key, com_type=ComType.pause)
            worker.drop_all_req()
            worker.req_queue.put(req)

    def resume(self, key):
        if key in self._workers:
            worker = self._workers[key]
            worker.is_ready.set()
            req = ReqData(key=key, com_type=ComType.resume)
            worker.req_queue.put(req)

    def state(self, key):
        if key in self._workers:
            worker = self._workers[key]
            if worker.is_stopping:
                return
            req = ReqData(key=key, com_type=ComType.state)
            worker.req_queue.put(req)

    def results(self, key):
        if key in self._workers:
            worker = self._workers[key]
            if worker.is_stopping:
                return
            req = ReqData(key=key, com_type=ComType.results)
            worker.req_queue.put(req)

    def finish(self, key):
        if key in self._workers:
            worker = self._workers[key]
            worker.is_stopping = True
            req_result = ReqData(key=key, com_type=ComType.results)
            req_stop = ReqData(key=key, com_type=ComType.stop)
            worker.req_queue.put(req_result)
            worker.req_queue.put(req_stop)

    def stop(self, key):
        if key in self._workers:
            worker = self._workers[key]
            worker.is_stopping = True
            worker.is_ready.clear()
            req = ReqData(key=key, com_type=ComType.stop)
            worker.drop_all_req()
            worker.req_queue.put(req)

    def is_installed(self, key):
        if self._workers.get(key, None):
            return True
        else:
            return False

    def is_busy(self, key):
        worker = self._workers.get(key, None)
        if worker.req_queue.empty() and worker.is_ready.is_set():
            return False
        return True
        
    def get_communicator(self, key):
        return self._workers[key].com
        
    def check_workers(self):
        """Check processis, end terminate finished"""
        for key, worker in self._workers.items():
            if worker.is_stopped():
                del self._workers[key]
                return key
        return None

    def terminate(self):
        for key in self._workers:
            self._workers[key].stop()
