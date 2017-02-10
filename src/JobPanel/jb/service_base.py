import subprocess
import async_repeater as ar

class ServiceStarter:
    def __init__(self):
        pass

    def start_pbs(self):
        pass

class ActionProcessor:
    def call_action(self, action, data):
        try:
            action_method = getattr(self, action)
        except  AttributeError:
            answer = {'error': 'Invalid action: %s' % (action)}
        else:
            answer = action_method(data)
        return answer

class ChildServiceProxy(ActionProcessor):
    """
    Auxiliary class to store state of a child service.

    Can keep status, near history, downloaded data, etc.
    Should be probably implemented by ServiceBase child classes.
    """
    def __init__(self, child_id, service):
        self.child_id = child_id
        self.service = service

    def make_ping(self):
        self.service.repeater.send_request(
            target=[self.child_id],
            data={'action': 'ping'},
            on_answer={'action': 'on_answer_ok'})

    def on_answer_no_error(self, data):
        pass

    def on_answer_ok(self, data):
        answer_data=data[1]
        print(answer_data)
        print("answer: OK")
        pass


class ServiceBase(ActionProcessor):
    """
    Process requests and answers.

    Main event processing loop is started by method 'run'.
    Event types are: request, answer;
    An event is processed by calling the action method with name given
    by the event data.

    Request format:
    { 'action': 'request_*', 'data': <data to be passed to the remote called request function> }

    service.request_method(self, request_data)

    Answer format:
    { 'data': <return value  of the remote request action>, 'error': <the error type string, details in a_data> }

    On_answer format:
    { 'action': 'on_answer_*', 'data': further data provided to the on_answwer function with answer data> }

    service.on_answer_method(self, child_id, request_data, answer_data, oa_data)

    """
    answer_ok = { 'data' : 'ok' }

    def __init__(self, service_address, listen_port):
        self.child_services={}
        self.repeater = ar.AsyncRepeater(service_address, listen_port)

    def get_listen_port(self):
        return self.repeater.listen_port


    def make_child_proxy(self, child_id, service):
        return ChildServiceProxy(child_id, service)


    def process_answers(self):
        for answer_data in self.repeater.get_answers():
            child_id = answer_data.sender[0]
            on_answer = answer_data.on_answer
            answer = answer_data.answer
            if (hasattr(answer, 'error')):
                self.child_services[child_id].error_answer(answer_data)
            self.child_services[child_id].call_action(on_answer['action'], ( on_answer['data'],  answer['data'] ))
        return

    def process_requests(self):
        for request_data in self.repeater.get_requests():
            (id, action, data) = request
            request = request_data.request
            answer = self.call_action(request['action'], request['data'])
            self.repeater.send_answer(answer)
        return

    """"""
    def request_start_child(self, request_data):
        address = request_data['socket_address']
        child_id = self.repeater.connect_child_repeater(self, address)
        self.child_services[child_id] = self.make_child_proxy(child_id, self)
        return self.answer_ok


    def request_stop_child(self, request_data):
        id = request_data['child_id']
        self.repeater.send_request([id], {'action' :' stop'}, { 'action' : 'on_answer_stop_child', 'data' : id})

    #def on_answer_stop_child(self, ):
    #    self.repeater.close_child_repeater(id)
    #    return self.answer_ok


    def request_ping(self, data):
        return self.answer_ok

    def request_stop(self, data):
        self.closing = True
        return {'data' : 'closing'}


