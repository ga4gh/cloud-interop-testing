from bravado.requests_client import RequestsClient
from wes_client.util import run_wf
from wes_client.util import cancel_wf
from wes_client.util import get_status
from wes_client.util import get_wf_details
from wes_client.util import get_wf_list
from wes_client.util import get_service_info as get_info

# arvclient = WESClient(config.wes_config['arvados-wes'])
# cromclient = WESClient(config.wes_config['hca-cromwell'])


class WESClient(object):
    def __init__(self, service):
        self.host = service['host']
        self.auth = service['auth']
        self.auth_type = service['auth_type']
        self.proto = service['proto']
        self.http_client = RequestsClient()

    def get_service_info(self):
        return get_info(self.http_client, self.auth, self.proto, self.host)

    def get_workflow_list(self):
        return get_wf_list(self.http_client, self.auth, self.proto, self.host)

    def run_workflow(self, wf, json, attachments):
        return run_wf(wf,
                      json,
                      attachments,
                      self.http_client,
                      self.auth,
                      self.proto,
                      self.host)

    def cancel_workflow(self, run_id):
        return cancel_wf(run_id, self.http_client, self.auth, self.proto, self.host)

    def get_workflow_run(self, run_id):
        return get_wf_details(run_id,
                              self.http_client,
                              self.auth,
                              self.proto,
                              self.host)

    def get_workflow_run_status(self, run_id):
        return get_status(run_id,
                          self.http_client,
                          self.auth,
                          self.proto,
                          self.host)


# import json
# client = WESClient(config.wes_config()['local'])
# i = client.get_workflow_run_status("3af08b20ddf44a34973ab228188b0156")
# print(i['state'])
# j = client.get_workflow_run("3af08b20ddf44a34973ab228188b0156")
# print(json.dumps(j, indent=4))
