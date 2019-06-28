from typing import Optional, Union, List

from common.analysis import data
from common.analysis import action_base as base
import enum

class Status(enum.IntEnum):
    none = 0
    composed = 1
    assigned = 2
    determined = 3
    ready = 4
    submitted = 5
    running = 6
    finished = 7


class Atomic:
    def __init__(self, action: 'base._ActionBase', inputs: List['Atomic'] = []):
        self.action = action
        # Action (like function definition) of the task (like function call).
        self.inputs = inputs
        # Input tasks for the action's arguments.
        for input in inputs:
            assert isinstance(input, Atomic)
            input.outputs.append(self)
        self.outputs: List['Atomic'] = []
        # List of tasks dependent on the result. (Try to not use and eliminate.)
        result: Optional[data.DataType] = None
        # Result of the task.
        self.id: int = 0
        # Task is identified by the hash of the hash of its parent task and its name within the parent.
        self.parent: Optional['Composed'] = None
        # parent task, filled during expand
        self.status = Status.none
        # Status of the task, possibly need not to be stored explicitly.
        self._result = None
        # The task result.
        self.resource_id = None

        self.start_time = -1
        self.end_time = -1
        self.eval_time = 0

    @property
    def priority(self):
        return 1

    @property
    def result(self):
        return self._result

    def evaluate(self):
        assert self.is_ready()
        data_inputs = [i.result for i in self.inputs]
        self._result = self.action.evaluate(data_inputs)
        self.status = Status.finished
        assert self.result is not None

    def is_finished(self):
        return self.result is not None

    def is_ready(self):
        """
        Update ready status, return
        :return:
        """
        if self.status < Status.ready:
            is_ready = all([task.is_finished() for task in self.inputs])
            if is_ready:
                self.status = Status.ready
        return self.status == Status.ready

    def set_id(self, parent_task, child_id):
        self.parent = parent_task
        self.id = data.hash(child_id, previous=parent_task.id)

    def __lt__(self, other):
        return self.priority < other.priority

class ComposedHead(Atomic):
    """
    Auxiliary task for the inputs of the composed task. Simplifies
    expansion as we need not to change input and output links of outer tasks, just link between head and tail.
    """
    @property
    def result(self):
        return self.inputs[0].result


class Composed(Atomic):
    """
    Composed tasks are non-leaf vertices of the execution tree.
    The Evaluation class takes care of their expansion during execution according to the
    preferences assigned by the Scheduler. It also keeps a map from
    """

    def __init__(self, action: 'base._ActionBase', inputs: List['Atomic'] = []):
        heads = [ComposedHead(base.Pass(), [input]) for input in inputs]
        super().__init__(action, heads)
        self.time_estimate = 0
        # estimate of the start time, used as expansion priority
        self.childs: Atomic = None
        # map child_id to the child task, filled during expand.

    def is_ready(self):
        """
        Block submission of unexpanded tasks.
        :return:
        """
        return self.is_expanded() and Atomic.is_ready(self)


    def child(self, item: Union[int, str]) -> Optional[Atomic]:
        """
        Return subtask given by parameter 'item'
        :param item: A unique idenfication of the subtask. The name of the
        action_instance within a workflow, the loop index for ForEach and While actions.
        :return: The subtask or None if the item is no defined.
        """
        assert self.childs
        return self.childs.get(item, None)

    def invalidate(self):
        """
        Invalidate the task and its descendants in the execution DAG using the call tree.
        :return:
        """

    def is_expanded(self):
        return self.childs is not None

    def expand(self):
        """
        Composed task expansion.

        Connect the head tasks to the body and the 'self' (i.e. the tail task) to the result
        action instance of the body. Auxiliary tasks for the heads, result and tail
        are used in order to minimize modification of the task links.

        :return: List of child tasks or None if the expansion can not be performed.
        Empty list is valid result, used to indicate end of a loop e.g. in the case of ForEach and While actions.
        """
        assert hasattr(self.action, 'expand')
        # Disconnect composed task heads.
        heads = self.inputs.copy()
        for head in heads:
            head.outputs = []
        # Generate and connect body tasks.
        self.childs = self.action.expand(self.inputs)
        if self.childs:
            for name, child in self.childs.items():
                child.set_id(self, name)

            result_task = self.childs['__result__']
            assert len(result_task.outputs) == 0
            result_task.outputs.append(self)
            self.inputs = [result_task]

        else:
            # No expansion: reconnect heads
            for head in heads:
                head.outputs = [self]

        return self.childs

    def evaluate(self):
        assert self.is_ready()
        assert len(self.inputs) == 1
        assert self.inputs[0].action.name == "_ResultAction"

        self._result = self.inputs[0].result
        self.status = Status.finished
        assert self.result is not None



