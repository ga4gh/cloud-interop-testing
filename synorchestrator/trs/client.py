import logging
import urlparse
import os

from bravado.requests_client import RequestsClient
from bravado.client import SwaggerClient

from synorchestrator.config import trs_config

logger = logging.getLogger(__name__)


def _get_trs_opts(service_id):
    """
    Look up stored parameters for tool registry services.
    """
    return trs_config()[service_id]


def _init_http_client(service_id=None, opts=None):
    """
    Initialize and configure HTTP requests client for selected service.
    """
    auth_header = {'token': 'Authorization',
                   'api_key': 'X-API-KEY',
                   None: ''} 
    if service_id:
        opts = _get_trs_opts(service_id)

    http_client = RequestsClient()
    split = urlparse.urlsplit('%s://%s/'.format(opts['proto'], opts['host']))

    http_client.set_api_key(host=opts['host'],
                            api_key=opts['auth'],
                            param_name=auth_header[opts['auth_type']],
                            param_in='header')
    return http_client


def load_trs_client(service_id, http_client=None):
    """
    Return an API client for the selected workflow execution service.
    """
    if http_client is None:
        http_client = _init_http_client(service_id=service_id)
    
    spec_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                             'ga4gh-tool-discovery.yaml')
    spec_client = SwaggerClient.from_url('file:///{}'.format(spec_path), 
                                         http_client=http_client)
    return spec_client.GA4GH



