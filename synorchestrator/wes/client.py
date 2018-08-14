import logging
import urlparse
import os

from bravado.requests_client import RequestsClient
from bravado.client import SwaggerClient

from synorchestrator.config import wes_config

logger = logging.getLogger(__name__)


def _get_wes_opts(service_id):
    """
    Look up stored parameters for workflow execution services.
    """
    return wes_config()[service_id]


def _init_http_client(service_id=None, opts=None):
    """
    Initialize and configure HTTP requests client for selected service.
    """
    auth_header = {'token': 'Authorization',
                   'api_key': 'X-API-KEY',
                   None: ''} 
    if service_id:
        opts = _get_wes_opts(service_id)

    http_client = RequestsClient()
    split = urlparse.urlsplit('{}://{}/'.format(opts['proto'], opts['host']))

    http_client.set_api_key(host=opts['host'],
                            api_key=opts['auth'],
                            param_name=auth_header[opts['auth_type']],
                            param_in='header')
    return http_client
    

class WESClient(object):
    """
    Adapter class for the WES client functionality from the 
    workflow-service library.
    """
    def __init__(self, service, http_client):
        from wes_client.util import run_wf
        from wes_client.util import cancel_wf
        from wes_client.util import get_status
        from wes_client.util import get_wf_details
        from wes_client.util import get_wf_list
        from wes_client.util import get_service_info

        self.host = service['host']
        self.auth = service['auth']
        self.auth_type = service['auth_type']
        self.proto = service['proto']
        self.http_client = http_client

    def GetServiceInfo(self):
        return get_service_info(self.http_client,
                                self.auth,
                                self.proto,
                                self.host)
    
    def ListRuns(self):
        return get_wf_list(self.http_client,
                           self.auth,
                           self.proto,
                           self.host)
    
    def RunWorkflow(self, request):
        return run_wf(workflow_file=request['workflow_url'],
                      jsonyaml=request['workflow_params'],
                      attachments=request['attachment'],
                      http_client=self.http_client,
                      auth=self.auth,
                      proto=self.proto,
                      host=self.host)
    
    def CancelRun(self, run_id):
        return cancel_wf(run_id,
                         self.http_client,
                         self.auth,
                         self.proto,
                         self.host)
    
    def GetRunStatus(self, run_id):
        return get_status(run_id,
                          self.http_client,
                          self.auth,
                          self.proto,
                          self.host)
    
    def GetRunLog(self, run_id):
        return get_wf_details(run_id,
                              self.http_client,
                              self.auth,
                              self.proto,
                              self.host)


def load_wes_client(service_id, http_client=None, client_library=None):
    """
    Return an API client for the selected workflow execution service.
    """
    if http_client is None:
        http_client = _init_http_client(service_id=service_id)

    if client_library is not None:
        return WESClient(service=_get_wes_opts(service_id), 
                         http_client=http_client)

    spec_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                             'workflow_execution_service.swagger.yaml')
    spec_client = SwaggerClient.from_url('file:///{}'.format(spec_path), 
                                         http_client=http_client)
    return spec_client.WorkflowExecutionService
