
class Scheduler:
    def __init__(self, tasks_dag):
        """

        :param tasks_dag: Tasks to be evaluated.
        """

class Evaluation:


class Task:
    def __init__(self, action, inputs):
        self._action = action
        self._inputs = inputs
        self._result = None
        self._last_input_hash = None

    def run(self):
        input_data = _List(*[i._result for i in self._inputs])
        input_data_hash = input_data.hash()
        if self._last_input_hash and self._last_input_hash == input_data_hash:
            return self._result
        else:
            self._result = action.evaluate(input_data)
            self._last_input_hash = input_data_hash
        return self._result

class ComposedTask(Task):
    """
    Task container that can not be evaluated, but can be expanded.
    """

    def run(self):
        assert False

    def expand(self):
        pass