class Users():
    def __init__(self, name,  to_pc, to_remote):
        self.name = name
        self.to_pc = to_pc
        self.to_remote = to_remote
        
    def get_login(self, password, key, is_remote):
        if is_remote and not self.to_remote:
            return ""
        if not self.to_pc:
            return None
        return password
        
    def save_communicator_login(self, password, is_remote):
        """return password and key for saving"""
        if is_remote and not self.to_remote:
            return "", "abc"
        return password, "xyz"
        
    def save_login(self, password):
        """return password and key for saving"""
        return password, "xzy"
