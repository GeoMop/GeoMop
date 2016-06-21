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
from geomop_project import Project
import shutil
import os
import flow_util


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
        if not bussy:
            bussy = bussy or self._check_stopped()
        if not bussy:
            bussy = bussy or self._check_terminated()
        if  bussy:
            return
        delete_key = []
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
                   delete_key.appen(key)
        for key in delete_key:
            self.run_jobs.remove(key)
            self._workers.remove(key)

            
    def _start_first(self):
        """start first job in queue and return True else return False"""
        for  key in  self.start_jobs:
            if not key in self._workers:
                mj = self._data_app.multijobs[key]
                analysis = self._reload_project(mj)
                conf_builder = ConfigBuilder(self._data_app)
                app_conf = conf_builder.build(key, analysis)
                com = Communicator(app_conf)
                worker = ComWorker(key, com)
                self._workers[worker.key] = worker
                worker.start()
                return True
        return False
        
    def _reload_project(self, data):
        """reload project files and return analysis"""
        # sync mj analyses + files
        analysis = None
        if Project.current is not None:
            mj_name = data.preset.name
            mj_dir =inst.Installation.get_config_dir_static(mj_name)
            proj_dir = Project.current.project_dir
            
            # get all files used by analyses
            files = []
            for analysis in Project.current.get_all_analyses():
                files.extend(analysis.files)

            analysis = Project.current.get_current_analysis()
            assert analysis is not None, "No analysis file exists for the project!"

            # copy the entire folder
            shutil.rmtree(mj_dir, ignore_errors=True)
            try:
                shutil.copytree(proj_dir, mj_dir)
                # remove result dir
                shutil.rmtree(os.path.join(mj_dir, "analysis_results"),
                    ignore_errors=True)
                # remove project file
                os.remove(os.path.join(mj_dir,".project"))
            # Directories are the same
            except shutil.Error as e:
                ComWorker.get_loger().error("Failed to copy project dir: " + str(e))
            # Any error saying that the directory doesn't exist
            except OSError as e:
                ComWorker.get_loger().error("Failed to copy project dir: " + str(e))

            # fill in parameters and copy the files
            for file in set(files):
                src = os.path.join(proj_dir, file)
                dst = os.path.join(mj_dir, file)
                # create directory structure if not present
                dst_dir = os.path.dirname(dst)
                if not os.path.isdir(dst_dir):
                    os.makedirs(dst_dir)
                flow_util.analysis.replace_params_in_file(src, dst, analysis.params)
        return analysis


    def _resume_first(self):
        """resume first job in queue and return True else return False"""
        for  key in  self.resume_jobs:
            if not key in self._workers:
                mj = self._data_app.multijobs[key]
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
                elif worker.is_interupted(self) or worker.is_error(self):
                    mj = self._data_app.multijobs[key]
                    if worker.is_interupted(self):
                        mj.get_state().set_status(TaskStatus.interupted)
                    else:
                        mj.get_state().set_status(TaskStatus.error)
                        mj.error = worker.get_error()
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
                elif worker.is_interupted(self) or worker.is_error(self):
                    mj = self._data_app.multijobs[key]
                    if worker.is_interupted(self):
                        mj.get_state().set_status(TaskStatus.interupted)
                    else:
                        mj.get_state().set_status(TaskStatus.error)
                        mj.error = worker.get_error()
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
        delete_key = []
        for  key in  self.stop_jobs:
            if key in self._workers:
                worker = self._workers[key]
                if worker.is_stopped():
                    self.run_jobs.append(key)
                    delete_key.append(key)
                    mj = self._data_app.multijobs[key]
                    if worker.is_error(self):
                        mj.get_state().set_status(TaskStatus.error)
                    else:
                        mj.get_state().set_status(TaskStatus.stopped)
                    self.state_change_jobs.append(key)
            else:
                ComWorker.get_loger().error("MultiJob {0} can't be stopped, run record is not found")
                delete_key.append(key)
                break
        for key in delete_key:
            self.stop_jobs.remove(key)
            self.run_jobs.remove(key)
            self._workers.remove(key)

    def _check_terminated(self):
        """
        check all job in resume queue, move resumed to run 
        queue and send get_state message. Update job states.
        """
        delete_key = []
        for  key in  self.terminate_jobs:
            if key in self._workers:
                worker = self._workers[key]
                if worker.is_stopped():
                    self.run_jobs.append(key)
                    delete_key.append(key)
                    mj = self._data_app.multijobs[key]
                    if worker.is_error(self):
                        mj.get_state().set_status(TaskStatus.error)
                    else:
                        mj.get_state().set_status(TaskStatus.stopped)
                    self.state_change_jobs.append(key)
            else:
                ComWorker.get_loger().error("MultiJob {0} can't be terminated, run record is not found")
                delete_key.append(key)
                break
        for key in delete_key:
            self.terminate_jobs.remove(key)
            self.run_jobs.remove(key)
            self._workers.remove(key)
        
    def _set_state(self, key, state, error):
        """
        Set state for set job
        """

    def pause_all(self):
        """Pause all running and starting jobs (use when app is closing)."""
        pass
        
    def stop_all(self):
        """stop all running and starting jobs"""
        pass
