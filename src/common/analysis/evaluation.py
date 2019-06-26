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
from typing import Any, List, Optional
import attr
import heapq
import numpy as np
import time


import common.analysis.data as data
import common.analysis.action_base as base
from common.analysis import dfs
from common.analysis.action_workflow import _Workflow
from common.analysis import task as task_mod
import common.analysis.action_instance as instance


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

    # def assign_task(self, task, i_thread=None):
    #     """
    #     Just evaluate tthe task immediately.
    #     :param task:
    #     :param i_thread:
    #     :return:
    #     """
    #     task.evaluate()
    #
    # def assign_mpi_task(self, task, n_mpi_procs=None):
    #     pass

    def get_finished(self):
        """
        Return list of the tasks finished since the last call.
        :return:
        """
        finished = self._finished
        self._finished = []
        return finished

    def submit(self, task):
        is_ready = task.is_ready()
        assert task.status >= task_mod.Status.ready
        if is_ready:
            task.evaluate()
            self._finished.append(task)
            #self._evaluate(task)

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




class Scheduler:
    def __init__(self, resources:Resource):
        """
        :param tasks_dag: Tasks to be evaluated.
        """
        self.resources = resources
        # Dict of available resources

        self.tasks = {}
        # all not yet sumitted tasks, vertices of the DAG that is optimized by the scheduler
        # maps task ID to the task

        self._ready_queue = []
        # Priority queue of the 'ready' tasks.  Used to submit the ready tasks without
        # whole DAG optimization. Priority is the

        self._start_time = time.clock()
        # Start time of the DAG evaluation.

        self._topology_sort = []
        # Topological sort of the tasks.

    @property
    def n_assigned_tasks(self):
        return len(self.tasks)

    def get_time(self):
        return time.clock() - self._start_time

    def append(self, tasks):
        """
        Add more tasks of the same DAG to be scheduled to the resources,
        :param tasks: All tasks that are new or have changed inputs.
        :return: List of composed tasks to expand. If empty the optimization should be called.
        """
        self.tasks.update({ t.id: t for t in tasks})

    def ready_queue_push(self, task):
        if task.is_ready():
            heapq.heappush(self._ready_queue, task)



    def _collect_finished(self):
        # collect finished tasks, update ready queue
        finished = []
        for resource in self.resources:
            new_finished = resource.get_finished()
            for task in new_finished:
                for dep_task in task.outputs:
                    self.ready_queue_push(dep_task)
            finished.extend(new_finished)
        return finished


    def update(self):
        """
        Update resources, collect finished tasks, submit new ready tasks.
        Should be called approximately every 'call_period' seconds.
        """
        finished = self._collect_finished()
        while self._ready_queue:
            task = heapq.heappop(self._ready_queue)
            if task.id in self.tasks:   # deal with duplicate entrieas in the queue
                self.resources[task.resource_id].submit(task)
                del self.tasks[task.id]
        return finished

    def optimize(self):
        """
        Perform CPM on the DAG of non-submitted tasks.
        Assign start_times and priorities according to the slack time.
        Assume just a single resource.
        :return:
        """
        # perform topological sort
        def predecessors(task):
            if task.is_finished():
                return []
            else:
                max_end_time = 0
                for pre in task.inputs:
                    max_end_time = max(max_end_time, pre.start_time + pre.eval_time)
                task.start_time = max_end_time
            return task.inputs

        def post_visit(task):
            task.resource_id = 0
            self.ready_queue_push(task)
            self._topology_sort.append(task)


        dfs.DFS(neighbours=predecessors,
                postvisit=post_visit).run(self.tasks.values())

        print("N task: ", len(self.tasks))



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
    """/
    The class for evaluation of a workflow.
    - perform expansion of composed tasks into the task DAG
    - can evaluate a workflow in interaction with the Scheduler
    - hierarchical view of the execution DAG, tasks are organised to the tree of composed tasks
      currently all tasks are kept, in future, just a map from the task address in the tree to its input hash would be
      enough computing results of the micro action on the fly
    - grouping of actions into macro actions is done here as the part of the expansion process



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
    @staticmethod
    def make_analysis(action:base._ActionBase, inputs:List[data.DataType]):
        """
        Bind values 'inputs' as parameters of the action using the Value action wrappers,
        returns a workflow without parameters.
        :param action:
        :param inputs:
        :return: a bind workflow instance
        """
        assert not action.parameters.is_variadic()
        assert len(inputs) == action.parameters.size()
        bind_name = 'all_bind_' + action.name
        workflow = _Workflow(bind_name)

        bind_action = instance.ActionInstance.create(action)
        for i, input in enumerate(inputs):
            value_instance = instance.ActionInstance.create(base.Value(input))
            workflow.set_action_input(bind_action, i, value_instance)
            assert bind_action.arguments[i].status >= instance.ActionInputStatus.seems_ok
        workflow.set_action_input(workflow.result, 0, bind_action)
        return workflow









    def __init__(self, analysis:base._ActionBase):
        """
        Create object for evaluation of the analysis created from the workflow 'wf' using
        values 'inputs' as its arguments.
        :param analysis: an action without inputs
        """
        self.resources = [ Resource() ]
        self.scheduler = Scheduler(self.resources)
        self.result_db = ResultDB()


        self.final_task = analysis.task_class(analysis)
        self.final_task.set_id(self.final_task, '__root__')

        self.composed_id = 0
        # Auxiliary ID of composed tasks to break ties
        self.queue = []
        # Priority queue of the composed tasks to expand. Tasks are expanded until the task DAG is not
        # complete or number of unresolved tasks is smaller then given limit.
        self.enqueue(self.final_task)

        self.force_finish = False
        # Used to force end of evaluation after an error.
        self.error_tasks = []
        # List of tasks finished with error.


        # init scheduler
        self.tasks_update([self.final_task])

    def tasks_update(self, tasks):
        for t in tasks:
            self.estimate_task_eval_time(t)
        self.scheduler.append(tasks)

    def estimate_task_eval_time(self, task):
        """
        Estimate the task evaluation time using the action and result_db.
        :param task:
        :return:
        """
        if task.is_finished():
            task.eval_time = task._end_time - task._start_time
        else:
            task.time_estimate = 1

    def execute(self, assigned_tasks_limit = np.inf, process_tasks = np.inf):
        """
        Execute the workflow.
        :return:
        """
        while not self.force_finish:
            schedule = self.expand_tasks(assigned_tasks_limit)
            self.tasks_update(schedule)
            self.scheduler.update()
            self.scheduler.optimize()
            if  self.scheduler.n_assigned_tasks == 0:
                self.force_finish = True


        return self.final_task


    def enqueue(self, task: task_mod.Composed):
        heapq.heappush(self.queue, (self.composed_id, task.time_estimate, task))
        self.composed_id += 1


    def expand_tasks(self, assigned_tasks_limit):
        """
        Expand composed tasks until number of planed tasks in the scheduler is under the given limit.
        :return:
        """
        # Force end of evaluation before all tasks are finished, e.g. due to an error.
        schedule = []

        while self.queue and not self.force_finish and self.scheduler.n_assigned_tasks < assigned_tasks_limit:
            composed_id, time, composed_task = heapq.heappop(self.queue)
            # TODO: fix expand, it connects Slots not to heads, but to an _ActionBase instance.
            task_dict = composed_task.expand()
            print("Expanded: ", task_dict)
            for task in task_dict.values():
                if isinstance(task, task_mod.Composed):
                    self.enqueue(task)
                else:
                    schedule.append(task)
            self.tasks_update([composed_task])
        return schedule



    def extract_input(self):
        input_data = List(*[i._result for i in self._inputs])



