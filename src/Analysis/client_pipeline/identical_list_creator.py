class ILCreator():
    """
    This client site script can crete equal list of action, that
    is same with last processed files. And compare analisis
    files.
    """
    
    def __init__(self, anal_dir, old_anal_dir, pipeline_script, old_pipeline_script):
        """
        init
        :param string anal_dir: dir with pipeline data
        :param string old_anal_dir: dir with old pipeline data
        :param string pipeline_script: file name where is pipeline script
        :param string old_pipeline_script: file name where is old pipeline script
        """
        pass
        
    def create_equol_list(self, file):
        """
        Function return equal list
        
        :param string file: list is save to specified file
        """
        pass
        
    def get_same_files(self):
        """
        Function return array of file, that is not nesserly copy
        to remote.
        """
        pass
    
