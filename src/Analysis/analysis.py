class MultiJob:
    # Class reprezenting a running analysis.
    # 
    def __init__(self, analysis_data, resource):
        self._resource = resource
    
    def run():
        # Should implement infinite loop listening on stdin or some port
        # for requests
        analysis = create_analysis(analysis_data)
        analysis.start()
  
class AnalysisBase:
    # Class performing a evaluation of a metamodel.
    # That is any calculation involving running of a forward model or 
    # some other complex task.
    
    def __init__(self, input_data):
        # Constructor accepts the input data of the analysis.
        self._input_data = input_data
        pass
      
    def run_job()
        #
        
    def start()
        # Start evaluation of particular analysis. 
        # Has to be implemented in derived classes.
        pass

  
class TaskBase:
    # Task defines execution (possibly parallel) of particular application for particular data.
    # This base class just store a dictionary with the task data, provides its getter and 
    # specify the structure of the directory. It includes as the input data for the application as
    # the resource requests specific to the task or to the application.
    #
    # Particular child classes are specializations for particular application.
    # Child class can add some resource requests particular for application that can be derived 
    # from the input data, e.g. estimate of run time, memory request, etc. This should be done in the constructor of the child class.
    # 
    # 
    def __init__(self, task_definition):
        # The constructor. 
        # For the base class we just store the dictionary given by parameter
        # @task_definition, which contains data specific for the task. For its structure 
        # see @get_task_dict method.
        # Child class can add some resource requests specific to the application.
        self._task_definition = tast_definition
        self._job_info = None
    
    def make_job_info(...):
        # Fill self._job_info by extracting data from self._task_definition
        # and construct application specific automatic data. 
        # Is meant to be called after creation of JobProxy, which should pass some
        # specification of the resource used by the task. At least the task has to ask 
        # for particular application configuration on the resource.
        # Should be implemented in application specific child classes.
        # Implementation should be safe to be called multiple times.
        pass
      
    def get_task_definition():
        # Returns dictionary with task definition data.
        #
        # Obligatory keys:
        #    application_name (given in @task_definition) 
        #       String with unique identifier of the application.
        #       during formation of the job we look for the configuration of 
        #       this application on the target machine. The same application 
        #       can have different configuration (location, binary name, environment to set)
        #       for different machines.
        #    workdir (determined automatically, possibly overwritten by user)
        #       Working directory relative to the GeoMop jobs directory.
        #    input_data (provided by user through other parts of GeoMop's GUI) 
        #       Input data for the calculation, e.g. name of main input file.
        #    resource_request - A directory with resource requests specific to the task.
        #       All keys are optional and further can be added in future. These keys
        #       allows specification of resources for the task independently of particular
        #       running environment (e.g. PBS configuration).
        #       
        #       max_n_proc - maximum number of processes that the task can use 
        #       max_ppn - maximum number of processes per node
        #       min_memory_per_node - required memory per node       
        #       wall_time_estimate - estimate of wall time necessary to finish calculation
        #
        #       run_time_estimate - Estimate of the total run time when running sequentially.
        #       memory_estimate - Estimate of the total memory allocated when running sequentially. 
        #            This includes also footprint of application and libraries.
        return self._task_definition

    def get_job_info():
        # Returns dictionary with task data.
        # TODO:
        #    Clearly specify data given in @task_definition,
        #    data used by JobProxy and its implementation,
        #    data for internal task usage or future use.
        #    Rather introduce other method returning just 
        #    data used by JobProxy.
        #
        # Obligatory keys:
        #    executable path
        #       Path to the executable String with unique identifier of the application.
        #       during formation of the job we look for the configuration of 
        #       this application on the target machine. The same application 
        #       can have different configuration (location, binary name, environment to set)
        #       for different machines.
        #    arguments (set by particular task implementation according to the keys input_data and resource_request)s
        #       Arguments of the application. 
        #    workdir (determined automatically, possibly overwritten by user)
        #       Working directory relative to the GeoMop jobs directory.
        #    resource_request - A directory with resource requests specific to the task.
        #       All keys are optional and further can be added in future. These keys
        #       allows specification of resources for the task independently of particular
        #       running environment (e.g. PBS configuration).
        #       
        #       max_n_proc - maximum number of processes that the task can use 
        #       max_ppn - maximum number of processes per node
        #       min_memory_per_node - required memory per node       
        #       wall_time_estimate - estimate of wall time necessary to finish calculation
        #
        #       par_code_fraction - fraction of the code that can run is scalable, the 
        #            in the sense of Amdahl's law, this depends on application but also on the 
        #            type of calculation so 
        #       par_allocation_fraction - same as previous but for the memory, that is fraction of
        #            memory allocation that scales linearly  
        #       run_time_estimate - Estimate of the total run time when running sequentially.
        #       memory_estimate - Estimate of the total memory allocated when running sequentially. 
        #            This includes also footprint of application and libraries.
        #       use_mpi (property of application)
        return self._task_dict
    
      
    def get_job_info(info_request):
        # Fill application specific keys in the @info_request
        # and return result.
        # This can either be passive and just read some application logs
        # or maintain some sort of connection with application.
      
    
    
class JobProxy:
    # A class representing the exection of a task on particular resource.
    # General execution involves three different computers. The client where the JobProxy instance is created;
    # the frontend - remote system (e.g. through SSH connection), the Task is executed there; 
    # and finally the node where the application is executed.
    #
    # We assume that the frontend can open any port on the node without any firewalls, and 
    # there exists shared workspace (used for redirection of stdout).
  
    def __init__(self, task, resource):
        self._task = task
        self._resource = resource
        self.check_appriori_resource_request()
        pass
    
    def check_appriori_resource_request(self):
        # Check that task resource request is compatible with the job resource
        # so that we can execute the task. I also overwrites or complete resource
        # with data form resource request of the task.
        #
        # When the job is part of a multijob, the task may not be 
        # fully specified so some resource request keys are not known
        # when multijob is created, however we want to check that the task can 
        # be executed on given resource as soon as possible. To this end 
        # this method should be able to handle also partly specified tasks.
        pass
        
    def submit(self):
        # Submit the job for the execution.
        pass
      
    def cancel(self):
        # Cancel execution of the job. Always result in an error.
        pass
      
    def fetch_info(info_request):
        # Fetch information about job execution from the frontend.
        # @info_request contains keys that we want to obtain.
        # Values of the keys are ignored.
        # Return the same directory filled with values.
        #
        # Common keys:
        #    status - Status of the execution: 0 - created, 1 - submitted
        #        2 - running, 3 - finished, 4 - fetched to frontend
        #        5 - fetched to client
        #
        #    error - Error code (replace exception class), and error data
        #            Zero error code for no error.
        #
        #    submit_time - time of the submission
        #    start_time - when execution started
        #    wall_run_time - Period from start till the fetch.
        #    application_time - (future) Total consumed corehours.
        #    memory_usage - (future) Total allocated memory.
        #
        #    Further keys may be task specific. 
        pass

    def fetch_status(self):
        # Call fetch_info asking only for status.
        pass

    def fetch_results_begin(self, destination):
        # Starts fetching results to destination which could be
        # frontend or client. However for more complex running environments
        # this method may accept also different destinations.
        pass
    
    
    
class Job:
    # Derived from JobProxy, implements the methods on frontend.
    # For application specific operations call methods of task instance on frontend.
    def __init__(self, task, resource):
        