"""
"""
import logging
import os

from bravado.requests_client import RequestsClient
from bravado.swagger_model import Loader
from bravado.client import SwaggerClient

from wfinterop.config import wes_config

logger = logging.getLogger(__name__)


def _get_wes_opts(service_id):
    """
    Look up stored parameters for workflow execution services.

    :param str service_id:
    """
    return wes_config()[service_id]


def _init_http_client(service_id=None, opts=None):
    """
    Initialize and configure HTTP requests client for selected service.

    :param str service_id:
    :param dict opts:
    """
    if service_id:
        opts = _get_wes_opts(service_id)

    http_client = RequestsClient()
    http_client.set_api_key(host=opts['host'],
                            api_key=opts['auth'],
                            # param_name=auth_header[opts['auth_type']],
                            param_in='header')
    return http_client


class WESInterface:
    def GetServiceInfo(self):
        pass

    def ListRuns(self):
        pass

    def RunWorkflow(self):
        pass

    def CancelRun(self):
        pass

    def GetRunStatus(self):
        pass

    def GetRunLog(self):
        pass


class WESAdapter(WESInterface):
    """
    Adapter class for the WES client functionality from the
    workflow-service library.

    :param wes_client:
    """
    _wes_client = None

    def __init__(self, wes_client):
        self._wes_client = wes_client

    def GetServiceInfo(self):
        return self._wes_client.get_service_info()

    def ListRuns(self):
        return self._wes_client.list_runs()

    def RunWorkflow(self, request, parts=None):
        return self._wes_client.run(wf=request['workflow_url'],
                                    jsonyaml=request['workflow_params'],
                                    attachments=request['attachment'],
                                    parts=parts)

    def CancelRun(self, run_id):
        return self._wes_client.cancel(run_id=run_id)

    def GetRunStatus(self, run_id):
        return self._wes_client.get_run_status(run_id=run_id)

    def GetRunLog(self, run_id):
        return self._wes_client.get_run_log(run_id=run_id)


def load_wes_client(service_id, http_client=None, client_library=None):
    """
    Return an API client for the selected workflow execution service.
    """
    if http_client is None:
        http_client = _init_http_client(service_id=service_id)

    if client_library is not None:
        from wes_client.util import WESClient
        wes_client = WESClient(service=_get_wes_opts(service_id))
        return WESAdapter(wes_client)

    spec_path = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                             'workflow_execution_service.swagger.yaml')
    spec_path = os.path.abspath(spec_path)

    opts = _get_wes_opts(service_id)
    api_url = '{}://{}'.format(opts['proto'], opts['host'])

    loader = Loader(http_client, request_headers=None)
    spec_dict = loader.load_spec('file:///{}'.format(spec_path),
                                 base_url=api_url)
    spec_client = SwaggerClient.from_spec(spec_dict,
                                          origin_url=api_url,
                                          http_client=http_client,
                                          config={'use_models': False})

    return spec_client.WorkflowExecutionService
