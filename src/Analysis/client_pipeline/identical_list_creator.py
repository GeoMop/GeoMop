import json
from ..pipeline.identical_list import IdenticalList

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

    @staticmethod
    def create_identical_list(compare_list_old, compare_list_new):
        """Create identical list from two compare lists(hashes lists)."""
        old_swap = {v: k for k, v in compare_list_old.items()}
        il = {}
        for new_id, new_hash in compare_list_new.items():
            if new_hash in old_swap:
                il[new_id] = old_swap[new_hash]
        return IdenticalList(il)

    @staticmethod
    def save_compare_list(compare_list, file):
        """Save compare list(hashes list) to file."""
        err = []
        try:
            with open(file, 'w') as fd:
                json.dump(compare_list, fd, indent=4, sort_keys=True)
        except Exception as e:
            err.append("Compare list saving error: {0}".format(e))
        return err

    @staticmethod
    def load_compare_list(file):
        """Load compare list(hashes list) form file."""
        err = []
        compare_list = dict()
        try:
            with open(file, 'r') as fd:
                compare_list = json.load(fd)
        except Exception as e:
            err.append("Compare list loading error: {0}".format(e))
        return err, compare_list
