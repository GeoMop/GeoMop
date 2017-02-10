import threading
import Queue

class ExThread(threading.Thread):
    """
    Thread that pass an expection to the caller thread through
    call 'join_with_exception'.
    """


    def __init__(self):
        threading.Thread.__init__(self)
        self.__status_queue = Queue.Queue()

    def run_with_exception(self):
        """This method should be overriden."""
        raise NotImplementedError

    def run(self):
        """This method should NOT be overriden."""
        try:
            self.run_with_exception()
        except BaseException:
            self.__status_queue.put(sys.exc_info())
        self.__status_queue.put(None)

    def wait_for_exc_info(self):
        return self.__status_queue.get()

    def join_with_exception(self):
        ex_info = self.wait_for_exc_info()
        if ex_info is None:
            return
        else:
            raise ex_info[1]