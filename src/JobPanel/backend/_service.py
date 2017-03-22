class ServiceProxy:
    pass

class Service:

    def delegator_start_service(self, executor_config):
        executor  = JsonData.make_instance(executor_config)
        executor.exec()

    def delegator_kill_service(self, executor_config):
        executor = JsonData.make_instance(executor_config)
        executor.kill()

    def delegator_clean_workspace(self):
        pass

    def request_stop(self):
        pass

    def request_start_child(self, service_config):
        pass

    def get_state(self):
        pass