class ILCreator():
    """
    This client site script can crete identical and compare list of action.
    
    Compare list is list of all action and its hashes and is store in
    analysis folder for future comparations.
    
    Equal list is list of action same with last processed files. List
    contain new and old name of same actions and is sent to remote    
    for excluding ready actions from processing
    """
    
    def __init__(self, anal_dir, pipeline, old_compare_list=None):
        """
        init
        :param string anal_dir: dir with pipeline data
        :param string pipeline: file with pipeline script
        :param string old_compare_list: file with previous compare list
        """
        pass

    def get_compare_list(self, file):
        """create and save to file new compare list"""
        pass
    
    def create_identical_list(self, compare_list):
        """
        Function return equal list
        
        :param string file: list is save to specified file
        """
        pass

    
