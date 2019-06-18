"""
Evaluation of a workflow.
1. workflow is dynamically rewritten to the Task DAG
2. small tasks may be merged in this process
3. Evaluation of tasks is given by evaluate methods of actions.
4. Task is a mapping of its inputs to its outputs.
5. All task evaluations are stored in a database, with lookup by the hash of the task's input.
6. As the Task DAG is processed the tasks with the input in the database are skipped.
7. Hashes are long enough to have probability of the collision small enough, so we
    relay on equality of the data if the hashes are equal.
4. Tasks are assigned to the resources by scheduler,
"""
from typing import Any, List
import attr
import heapq

import common.analysis.data as data
import common.analysis.action_base as base
from common.analysis.action_workflow import _Workflow




class Resource:
    """
    Model for a computational resource.
    Resource can provide various kind of feautres specified by dictionary of tags with values None, int or string.
    A task (resp. its action) can specify requested tags, such task can be assigned only to the resource that
    have these tags and have value of an integer tag greater then value of the task.

    We shall start with fixed number of resources, dynamic creation of executing PBS jobs can later be done.

    """
    def __init__(self):
        """
        Initialize time scaling and other features of the resource.
        """
        self.start_latency = 0.0
        # Average time from assignment to actual execution of the task. [seconds]
        self.stop_latency = 0.0
        # Average time from finished task till assignment to actual execution of the task. [seconds]
        self.ref_time = 1.0
        # Average run time for a reference task with respect to the execution on the reference resource.
        self.n_threads = 1
        # Number of threads we can assign to the resource.
        self.n_mpi_proces = 0
        # Maximal number of MPI processes one can assign.
        self._finished = []

    def assign_task(self, task, i_thread=None):
        """
        Just evaluate tthe task immediately.
        :param task:
        :param i_thread:
        :return:
        """
        task.evaluate()

    def assign_mpi_task(self, task, n_mpi_procs=None):
        pass

    def finished(self):
        """
        Return list of the tasks finished since the last call.
        :return:
        """
        finished = self._finished
        self._finished = []
        return finished




class Scheduler:
    def __init__(self, resources:Resource):
        """
        :param tasks_dag: Tasks to be evaluated.
        """

    def update(self, tasks):
        """
        Add more tasks of the same DAG to be scheduled to the resources,
        :param tasks:
        :return:
        """



@attr.s(auto_attribs=True)
class Result:
    input: bytearray
    result: bytearray
    result_hash: int    # ints are of any size in Python3

    @staticmethod
    def make_result(input, result):
        input = data.serialize(input)
        result = data.serialize(result)
        res_hash = data.hash_fn(result)
        return Result(input, result, res_hash)

    def extract_result(self):
        return deserialize(self.result)


@attr.s(auto_attribs=True)
class Task:
    action: base._ActionBase
    inputs: List['Task']
    outputs: List['Task']
    result: data.DataType = None
    _id: int = None

    def evaluate(self):
        data_inputs = [i.result for i in self.inputs]
        assert all([i.is_finished() for i in data_inputs])
        self.result = self.action.evaluate(inputs=data_inputs)
        assert self.result is not None


    def is_finished(self):
        return self.result is not None


    def task_id(self) -> int:
        if self._id is None:
            self._id = 0
            for input_task in task.inputs:
                data.hash(input_task.task_id(), seed=self._id)
        return self._id


class ResultDB:
    """
    Simple result database.
    For an input hash find result, its environment and runtime, and result hash.
    """
    def __init__(self):
        self.result_dict = {}


    def get_result(self, input_hash):
        return self.result_dict.get(input_hash, None)


    def store_result(self, result: Result):
        input_hash = hash_fn(result.input)
        self.result_dict[input_hash] = result


class Evaluation:
    """
    The class for evaluation of a workflow.
    - perform rewriting workflows into the task DAG
    - use given scheduler to assign tasks to resources
    - keeps input and output hashes
    - implement reuse form previous evaluationevaluation
    """
    def __init__(self):
        self.resources = [ Resource() ]
        self.scheduler = Scheduler(self.resources)
        self.result_db = ResultDB()

    def execute_workflow(self, wf:_Workflow, inputs=[]):
        """
        Execute the 'wf' workflow for the data arguments given by 'inputs'.

        - Assign 'inputs' to the workflow inputs, effectively creating an analysis (workflow without inputs).
        - Expand the workflow to the Task DAG.
        - while not finished:
            expand_composed_tasks
            update scheduler

        We use Dijkstra algorithm (on incoplete graph) to process tasks according to the execution time on the reference resource.
        Tasks are identified by the hash of their inputs.
        :param wf:
        :param inputs:
        :return: List of all tasks.
        """
        force_finish = False
        # Force end of evaluation before all tasks are finished, e.g. due to an error.
        queue = []

        while self.queue and not force_finish:
            composed_task = heapq.heappop(queue)
            # TODO: expand composed task, add regular tasks to scheduler and new composed tasks to queue.



       
    def expand_task(virtual_task, dag):
       pass

    def extract_input(self):
        input_data = List(*[i._result for i in self._inputs])

    def _evaluate(self, task):
        """
        Evaluate the task using the input from the input tasks.
        :return:
        """

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