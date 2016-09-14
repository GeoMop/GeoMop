from geomop_util import Serializable
import config as cfg
import os

BASE_DIR = 'JobPanel'


class WorkspaceConf():
    """Workspace configuration"""
    last_id = 0    
    
    def __init__(self, **kwargs):
        def kw_or_def(key, default=None):
            return kwargs[key] if key in kwargs else default
        self.path = kw_or_def("path")
        """Workspace path"""
        self.id = kw_or_def("id")
        """Id for link to workspaces mj statisctics (name of mj dir)"""
        self.pc = kw_or_def("pc", os.uname()[1])
        """computer name"""
        self.selected_mj = kw_or_def("selected_mj", 0) 
        
    def save_workspace(self):
        """serialize workspace data to workspace settings directory"""
        pass

    def load_workspace(self):
        """
        deserialize workspace data to workspace settings directory
        
        :return: local workspace configuration and local presets
        """
        workspace_conf = None
        presets = None
        
        return workspace_conf, presets


class WorkspacesConf():
    """
    Known workspaces
    """
    DIR = "workspaces"
    FILE_NAME = "workspaces"

    __serializable__ = Serializable(
        composite={}
    )
    
    def __init__(self, **kwargs):
        def kw_or_def(key, default=None):
            return kwargs[key] if key in kwargs else default
        self.workspaces = kw_or_def("workspaces", [])
        """Workspaces array"""
        self.selected  = kw_or_def("selected")
        """selected workspace"""

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
        
    def save(self, selected_mj):
        """serialize settings"""
        if self.selected:
            self.workspaces[self.selected].selected_mj = selected_mj
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
        
    def save_to_workspace(self):
        """save selected workspace to workspace directory"""
        pass
        
    def get_selected_mj(self):
        """get mj selected during closing"""
        if self.selected:
            return self.workspaces[self.selected].selected_mj
        return 0

    def select_workspace(self, path):
        """
        select new workspace
        
        If workspace is not in array, import it. If import is OK, return True,
        elseif workspace is oh switch it
        else show error message return False and stay in old workspace.
        """
        path_exist = False
        path = self._get_compare_path(path)
        for i in range(0, len(self.workspaces)):
            if path == self.workspaces[i].path:
                self.selected = i
                path_exist = True
                break
        if not path_exist:
            # TODO import
            i = len(self.workspaces)
            self.workspaces.append(WorkspaceConf(path=path, id=i))
        return True
