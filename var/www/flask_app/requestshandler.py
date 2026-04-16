import json
from datetime import datetime
import uuid
import os 

class Data:
    def __init__(self, data):
        self.data = data

    @property
    def action(self):
        return self.data['action']

    @property
    def user(self):
        return self.data['user']

    @property
    def request_id(self):
        return self.data['request_id']

    @property
    def status(self):
        return self.data['status']



class RequestHandler:
    def __init__(self, request_id=None, status=None):
        if not request_id:
            self.request_id = str(uuid.uuid1())
            self.status = "idle"
        else:
            self.request_id = request_id
            self.status = status

    @property
    def data(self):
        filename = f"/var/www/flask_app/requests/{self.status}/{self.request_id}"
        data = json.load(open(filename))
        return Data(data)

    def create(self, action_name, payload, user):
        """
        :param payload: JSON doc
        """
        data = {}
        data["request_id"] = self.request_id
        data["status"] = self.status
        data["creation_time"] = datetime.utcnow().isoformat()
        data["action"] = action_name
        data["user"] = user
        data["payload"] = payload

        f = open(f"/var/www/flask_app/requests/idle/{self.request_id}","w")
        json.dump(data, f)

    def set_queued(self):
        idle_filename = f"/var/www/flask_app/requests/idle/{self.request_id}"
        data = json.load(open(idle_filename))
        data['queued_time'] = datetime.utcnow().isoformat()
        data['status'] = 'queued'
        self.status = "queued"
        queued_filename = f"/var/www/flask_app/requests/queued/{self.request_id}"
        json.dump(data, open(queued_filename, "w"))
        os.remove(idle_filename)

    def set_running(self):
        idle_filename = f"/var/www/flask_app/requests/queued/{self.request_id}"
        data = json.load(open(idle_filename))
        data['running_time'] = datetime.utcnow().isoformat()
        data['status'] = 'running'
        self.status = 'running'
        queued_filename = f"/var/www/flask_app/requests/running/{self.request_id}"
        json.dump(data, open(queued_filename, "w"))
        os.remove(idle_filename)

    def set_done(self):
        idle_filename = f"/var/www/flask_app/requests/running/{self.request_id}"
        data = json.load(open(idle_filename))
        data['done_time'] = datetime.utcnow().isoformat()
        data['status'] = 'done'
        self.status = 'done'
        queued_filename = f"/var/www/flask_app/requests/running/{self.request_id}"
        queued_filename = f"/var/www/flask_app/requests/done/{self.request_id}"
        json.dump(data, open(queued_filename, "w"))
        os.remove(idle_filename)

    def set_error(self):
        idle_filename = f"/var/www/flask_app/requests/running/{self.request_id}"
        data = json.load(open(idle_filename))
        data['error_time'] = datetime.utcnow().isoformat()
        data['status'] = 'error'
        self.status = 'error'
        queued_filename = f"/var/www/flask_app/requests/error/{self.request_id}"
        json.dump(data, open(queued_filename, "w"))
        os.remove(idle_filename)

    def execute(self):
        lib_entry_point = self.data.data['payload']['lib_entry_point']
        from importlib import import_module
        module, fn_name = lib_entry_point.rsplit(".", 1)
        action_module = import_module(module)
        action_func = getattr(action_module, fn_name)

        # to catch the stdout and stderr
        import io
        from contextlib import redirect_stdout, redirect_stderr
        out_buffer = io.StringIO()
        err_buffer = io.StringIO()
        with redirect_stdout(out_buffer), redirect_stderr(err_buffer):

            # to connect to OpenStack
            from apis.openstack_api.openstack_connection import OpenstackConnection
            with OpenstackConnection(self.data.data['payload']["cloud_account"]) as conn:
                output = action_func(conn, self.data.data)
        stdout_messages = out_buffer.getvalue()
        stderr_messages = err_buffer.getvalue()

        running_filename = f"/var/www/flask_app/requests/running/{self.request_id}"
        data = json.load(open(running_filename))
        data['stdout'] = stdout_messages.strip()
        data['stderr'] = stderr_messages.strip()
        data['output'] = output
        json.dump(data, open(running_filename, "w"))


class RequestHandlerList(list):

    def add(self, request_id, status):
        self.append(RequestHandler(request_id, status))

    def set_queued(self):
        for req in self.__iter__():
            req.set_queued()

    def set_running(self):
        for req in self.__iter__():
            req.set_running()

    def set_done(self):
        for req in self.__iter__():
            req.set_done()

    def set_error(self):
        for req in self.__iter__():
            req.set_error()


class RequestsManager:

    def get_idle(self):
        req_l = RequestHandlerList()
        for req_id in os.listdir('/var/www/flask_app/requests/idle'):
            req_l.add(req_id, "idle")
        return req_l

    def get_queued(self):
        req_l = RequestHandlerList()
        for req_id in os.listdir('/var/www/flask_app/requests/queued'):
            req_l.add(req_id, "queued")
        return req_l

    def get_running(self):
        req_l = RequestHandlerList()
        for req_id in os.listdir('/var/www/flask_app/requests/running'):
            req_l.add(req_id, "running")
        return req_l

    def get_done(self):
        req_l = RequestHandlerList()
        for req_id in os.listdir('/var/www/flask_app/requests/done'):
            req_l.add(req_id, "done")
        return req_l

    def get_error(self):
        req_l = RequestHandlerList()
        for req_id in os.listdir('/var/www/flask_app/requests/error'):
            req_l.add(req_id, "error")
        return req_l

    def get_all(self):
        req_l = RequestHandlerList()
        req_l += self.get_idle()
        req_l += self.get_queued()
        req_l += self.get_running()
        req_l += self.get_done()
        req_l += self.get_error()
        return req_l

    def get_by_id(self, request_id):
        """Finds a request by ID by checking all status subdirectories."""
        for status in ['idle', 'queued', 'running', 'done', 'error']:
            path = f"/var/www/flask_app/requests/{status}/{request_id}"
            if os.path.exists(path):
                return RequestHandler(request_id, status)
        return None


if __name__ == '__main__':

    m = RequestsManager()
    l = m.get_all()
    for r in l:
        data = r.data
        print(data.request_id)
        print(data.user)
        print(data.status)
        print(data.action)
        print("-----")
    

