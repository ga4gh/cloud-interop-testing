import logging

from bravado.requests_client import RequestsClient
from bravado.client import SwaggerClient
from synorchestrator.config import wes_config

logger = logging.getLogger(__name__)


def init_http_client(service_id=None, opts=None):
    """
    Initialize and configure HTTP requests client for selected service.
    """
    auth_header = {'token': 'Authorization',
                   'api_key': 'X-API-KEY'}
    if service_id:
        opts = wes_config[service_id]

    http_client = RequestsClient()

    http_client.set_api_key(
        host=opts['host'],
        api_key=opts['auth'],
        param_name=auth_header[opts['auth_type']],
        param_in='header'
    )
    return http_client


def load_wes_client(service_id=None, http_client=None):
    """
    Return an API client for the selected workflow execution service.
    """
    if http_client is None:
        http_client = init_http_client(service_id=service_id)
    return SwaggerClient.from_url('https://raw.githubusercontent.com/ga4gh/workflow-execution-service-schemas/develop/openapi/workflow_execution_service.swagger.yaml',
                                  http_client=http_client).WorkflowExecutionService
