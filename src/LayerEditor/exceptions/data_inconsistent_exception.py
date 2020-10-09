class DataInconsistentException(Exception):
    def __init__(self, message, errors):
        super(DataInconsistentException, self).__init__(message)
        self.errors = errors
