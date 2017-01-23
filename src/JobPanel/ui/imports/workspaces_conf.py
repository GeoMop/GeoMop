from geomop_util import Serializable
import ui.imports.ie_presets as ie
from ui.data.preset_data import EnvPreset, PbsPreset, ResPreset, SshPreset
from ui.data.mj_data import MultiJob, MultiJobPreset
from ui.dialogs.import_dialog import ImportDialog
from data.states import TaskStatus
from PyQt5 import QtWidgets

import config as cfg
import os
import uuid
import yaml
import time

BASE_DIR = 'JobPanel'
WORKSPACE_CONF_DIR = 'conf'


class WorkspaceConf():
    """Workspace configuration"""
    last_id = 0    
    
    class LocalConf():
        def __init__(self, **kwargs):
            def kw_or_def(key, default=None):
                return kwargs[key] if key in kwargs else default
            self.data = {}
            self.data['pc'] = kw_or_def("pc")            
            """computer name"""
            self.data['uuid'] = kw_or_def("uuid")
            """workspace uuid for checking"""            
    
    def __init__(self, **kwargs):
        def kw_or_def(key, default=None):
            return kwargs[key] if key in kwargs else default
        self.path = kw_or_def("path")
        """Workspace path"""
        self.id = kw_or_def("id")
        """Id for link to workspaces mj statisctics (name of mj dir)"""
        self.pc = os.uname()[1]
        """computer name"""
        self.selected_mj = kw_or_def("selected_mj", 0) 
        """last selected mj"""
        self.selected_analysis = kw_or_def("selected_analysis") 
        """last selected analysis"""
        self.uuid = kw_or_def("uuid",str(uuid.uuid4()))
        """workspace uuid for checking"""
        dir = os.path.join(self.path, WORKSPACE_CONF_DIR)
        if  os.path.isdir(self.path) and not os.path.isdir(dir):
            os.makedirs(dir)
        
    def save_workspace(self, presets):
        """serialize workspace data to workspace settings directory"""
        dir = os.path.join(self.path, WORKSPACE_CONF_DIR)
        conf = self.LocalConf(pc=self.pc, uuid=self.uuid)
        yaml_file = open(os.path.join(dir, 'workspace'), 'w')
        yaml.dump(conf.data, yaml_file)
        yaml_file.close()
        for cls_name, data in presets.items():
            name = cls_name[2:].lower()
            cls = getattr(ie, cls_name)
            instance = cls(os.path.join(dir, name))
            instance.export_(data)

    def import_workspace(self, mj_container):
        """
        deserialize presets from workspace data and import known mj 
        """
        if not os.path.isfile(os.path.join(self.path, WORKSPACE_CONF_DIR, 'workspace')):
            # new workspace
            return True
            
        config = self.get_config()
        file = os.path.join(self.path, WORKSPACE_CONF_DIR, 'mj')
        mj_imp = ie.IEMj(file)
        mj = mj_imp.import_(MultiJob(MultiJobPreset()))
        
        file = os.path.join(self.path, WORKSPACE_CONF_DIR, 'env')
        env_imp = ie.IEEnv(file)
        env = env_imp.import_(EnvPreset())
        file = os.path.join(self.path, WORKSPACE_CONF_DIR, 'pbs')
        pbs_imp = ie.IEPbs(file)
        pbs = pbs_imp.import_(PbsPreset())
        file = os.path.join(self.path, WORKSPACE_CONF_DIR, 'res')
        res_imp = ie.IERes(file)
        res = res_imp.import_(ResPreset())
        file = os.path.join(self.path, WORKSPACE_CONF_DIR, 'ssh')
        ssh_imp = ie.IESsh(file)
        ssh = ssh_imp.import_(SshPreset())
        valid_mj = {} 
        conf_env = []
        conf_pbs = []
        conf_res = []
        conf_ssh = []
        
        for key, mj in mj.items():
            path = os.path.join(self.path,mj.preset.analysis, "mj", mj.preset.name)
            if not os.path.isdir(path):
                continue
            # resource
            new_res = mj.preset.resource_preset
            # if some preset in res is changed, change res too
            is_known = True
            if not new_res in res:
                # invalid res
                continue
            if not new_res in mj_container.resource_presets or \
                not ie.IERes.cmp(res[new_res], mj_container.resource_presets[new_res]):                                
                is_known = False      
            # mj_ssh, mj_env
            new_mj_ssh = res[new_res].mj_ssh_preset            
            if new_mj_ssh is None:
                # is local, thet is same in both workspace -> not solve
                new_mj_env = None
            else:
                # if env preset in ssh is changed, change ssh too
                is_ssh_known = True
                if not new_mj_ssh in ssh:
                    # invalid ssh
                    continue
                if not new_mj_ssh in mj_container.ssh_presets or \
                    not ie.IESsh.cmp(ssh[new_mj_ssh], mj_container.ssh_presets[new_mj_ssh]):
                    is_known = False
                    is_ssh_known = False
                new_mj_env = ssh[new_mj_ssh].env
                if new_mj_env is None:
                    # invalid env
                    continue
                if not new_mj_env in mj_container.env_presets or \
                    not ie.IEEnv.cmp(env[new_mj_env], mj_container.env_presets[new_mj_env]):
                    is_known = False
                else:
                    new_mj_env = None
                    if is_ssh_known:
                        new_mj_ssh = None
                    
            # j_ssh, j_env
            new_j_ssh = res[new_res].j_ssh_preset
            if new_j_ssh is None:
                # is same as mj_env -> solved there
                new_j_ssh = None
                new_j_env = None
            else:
                # if env preset in ssh is changed, change ssh too
                is_ssh_known = True
                if not new_j_ssh in ssh:
                    # invalid ssh
                    continue
                if not new_j_ssh in mj_container.ssh_presets or \
                    not ie.IESsh.cmp(ssh[new_j_ssh], mj_container.ssh_presets[new_j_ssh]):
                    is_known = False
                    is_ssh_known = False
                new_j_env = ssh[new_j_ssh].env
                if new_j_env is None:
                    # invalid env
                    continue
                if not new_j_env in mj_container.env_presets or \
                    not ie.IEEnv.cmp(env[new_j_env], mj_container.env_presets[new_j_env]):
                    is_known = False
                else:
                    new_j_env = None
                    if is_ssh_known:
                        new_j_ssh = None
            # mj_pbs
            new_mj_pbs = res[new_res].mj_pbs_preset
            if new_mj_pbs is not None:
                if not new_mj_pbs in pbs:
                    # invalid pbs
                    continue
                if not new_mj_pbs in mj_container.pbs_presets or \
                    not ie.IEPbs.cmp(pbs[new_mj_pbs], mj_container.pbs_presets[new_mj_pbs]):
                    is_known = False
                else:
                    new_mj_pbs = None
            # mj_pbs
            new_j_pbs = res[new_res].j_pbs_preset
            if new_j_pbs is not None:
                if not new_j_pbs in pbs:
                    # invalid pbs
                    continue
                if not new_j_pbs in mj_container.pbs_presets or \
                    not ie.IEPbs.cmp(pbs[new_j_pbs], mj_container.pbs_presets[new_j_pbs]):
                    is_known = False
                else:
                    new_j_pbs = None
            # all is OK
            valid_mj[key] = mj        
            if not is_known:
                # remmember confusing presets
                if not new_res in conf_res:
                    conf_res.append(new_res)
                if new_mj_env is not None and not new_mj_env in conf_env:
                    conf_env.append(new_mj_env)
                if new_j_env is not None and not new_j_env in conf_env:
                    conf_env.append(new_j_env)
                if new_mj_ssh is not None and not new_mj_ssh in conf_ssh:
                    conf_ssh.append(new_mj_ssh)
                if new_j_ssh is not None and not new_j_ssh in conf_ssh:
                    conf_ssh.append(new_j_ssh)
                if new_mj_pbs is not None and not new_mj_pbs in conf_pbs:
                    conf_pbs.append(new_mj_pbs)
                if new_j_pbs is not None and not new_j_pbs in conf_pbs:
                    conf_pbs.append(new_j_pbs)
        if len(valid_mj)<1:
            # empty workspace
            return True           
        
        idialog = ImportDialog(None, self.path, valid_mj, config['pc'])
        result = idialog.exec_()
        if result != QtWidgets.QDialog.Accepted:
            return True
            
        # add confusing presets to mj container        
        prefix = idialog.get_prefix()
        for key in conf_res:
            resource = res[key] 
            resource.name = prefix + "_" + resource.name
            if resource.mj_ssh_preset is not None and \
                resource.mj_ssh_preset in conf_ssh:
                resource.mj_ssh_preset = prefix + "_" + resource.mj_ssh_preset
            if resource.j_ssh_preset is not None and \
                resource.j_ssh_preset in conf_ssh:
                resource.j_ssh_preset = prefix + "_" + resource.j_ssh_preset
            if resource.mj_pbs_preset is not None  and \
                resource.mj_pbs_preset in conf_pbs:
                resource.mj_pbs_preset = prefix + "_" + resource.mj_pbs_preset
            if resource.j_pbs_preset is not None  and \
                resource.j_pbs_preset in conf_pbs:
                resource.j_pbs_preset = prefix + "_" + resource.j_pbs_preset
            mj_container.resource_presets[resource.name] = resource
        for key in conf_ssh:
            ssh_con = ssh[key]
            ssh_con.name = prefix + "_" + ssh_con.name
            if ssh_con.env is not None and \
                ssh_con.env in conf_ssh:
                ssh_con.env = prefix + "_" + ssh_con.env
            mj_container.ssh_presets[ssh_con.name] = ssh_con
        for key in conf_pbs:
            pbs_conf = pbs [key]
            pbs_conf.name = prefix + "_" + pbs_conf.name
            mj_container.pbs_presets[pbs_conf.name] = pbs_conf
        for key in conf_env:
            environment = env[key]
            environment.name = prefix + "_" + environment.name
            mj_container.env_presets[environment.name] = environment  
            
        # construct and repair name of confusing presets in workspace config
        mj_container.multijobs.clear() 
        for key, mj in  valid_mj.items():
            if mj.preset.resource_preset in conf_res:
                mj.preset.resource_preset = prefix + "_" + mj.preset.resource_preset
            mj.error = "Multijob was processed from different location."
            mj.state.analysis = mj.preset.analysis
            mj.state.name = mj.preset.name
            mj.state.status = TaskStatus.error
            mj.state.estimated_jobs = 0
            mj.state.finished_jobs = 0
            mj.state.insert_time = time.time()
            mj.state.known_jobs = 0
            mj.state.queued_time = 0
            mj.state.run_interval = 0
            mj.state.running_jobs = 0
            mj.start_time = None
            mj.state.update_time = 0
            mj_container.multijobs[key] = mj
            mj_container.multijobs[key].preset.deleted_remote = True
        mj_container.save_all() 
        mj_container.backup_presets()
        return True
    
  

    def get_config(self):
        """
        deserialize config from workspace data        
        """
        file = os.path.join(self.path, WORKSPACE_CONF_DIR, 'workspace')
        if os.path.isfile(file):
            yaml_file = open(file, 'r')
            data= yaml.load(yaml_file)
            yaml_file.close()
            return data
        return None
    
    def check_config(self):
        """compare workspace signature for equolity confirmation"""
        config = self. get_config()
        if config is None:
            return True
        if config.uuid == self.uuid:
            return True
        return False

class WorkspacesConf():
    """
    Known workspaces
    """
    DIR = "workspaces"
    FILE_NAME = "workspaces"

    __serializable__ = Serializable(
        composite={'workspaces': WorkspaceConf}
    )
    
    def __init__(self, **kwargs):
        def kw_or_def(key, default=None):
            return kwargs[key] if key in kwargs else default
        self.workspaces = kw_or_def("workspaces", [])
        """Workspaces array"""
        self.selected  = kw_or_def("selected")
        """selected workspace"""
        if  self.selected is not None and self.selected >= len(self.workspaces):
            if  len(self.workspaces) == 0:
                self.selected = None
            else:
                self.selected = 0

    @property
    def workspace(self):
        """Application main window."""
        return self.workspaces[self.selected].path
        
    @staticmethod
    def _get_compare_path(path):
        """return uppercase normalized real path"""
        if path is None:
            return None
        res=os.path.realpath(path)
        return os.path.normcase(res)
    
    def get_id(self):
        """get id selected mj"""
        if self.selected  is None:
            return 0        
        return self.workspaces[self.selected].id
        
    def get_path(self):
        """get path selected mj"""
        if self.selected  is None:
            return None
        return self.workspaces[self.selected].path
        
    def save(self, selected_mj, selected_analysis):
        """serialize settings"""
        if self.selected:
            self.workspaces[self.selected].selected_mj = selected_mj
            self.workspaces[self.selected].analysis = selected_analysis
        directory = os.path.join(BASE_DIR, self.DIR)
        cfg.save_config_file(self.FILE_NAME, self, directory)
    
    @classmethod
    def open(cls):
        """deserialize settings"""    
        directory = os.path.join(BASE_DIR, cls.DIR)
        config = cfg.get_config_file(cls.FILE_NAME, directory, cls=WorkspacesConf)
        if config is None:
            config =  WorkspacesConf()
        return config
        
    def save_to_workspace(self, presets):
        """save selected workspace to workspace directory"""
        self.workspaces[self.selected].save_workspace(presets)
        
    def get_selected_mj(self):
        """get mj selected during closing"""
        if self.selected:
            return self.workspaces[self.selected].selected_mj
        return 0
        
    def get_selected_analysis(self):
        """get analysis from selected mj"""
        if self.selected:
            return self.workspaces[self.selected].selected_analysis
        return 0

    def select_workspace(self, path, mj_container):
        """
        select new workspace
        
        If workspace is not in array, import it. If import is OK, return True,
        elseif workspace is oh switch it
        else show error message return False and stay in old workspace.
        """
        path_exist = False
        path = self._get_compare_path(path)
        if path == self. get_path():
            return False
        for i in range(0, len(self.workspaces)):
            if path == self.workspaces[i].path:
                self.selected = i
                path_exist = True
                break
        if not path_exist:
            i = len(self.workspaces)
            self.selected = i
            self.workspaces.append(WorkspaceConf(path=path, id=i))
            return self.workspaces[self.selected].import_workspace(mj_container)
        return True
