import logging
import urlparse

from bravado.requests_client import RequestsClient
from bravado.client import SwaggerClient

logger = logging.getLogger(__name__)


def _get_trs_opts(service_id, trs_config=None):
    """
    Look up stored parameters for tool registry services.
    """
    return trs_config[service_id]


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

    http_client.set_api_key(
        host=opts['host'],
        api_key=opts['auth'],
        param_name=auth_header[opts['auth_type']],
        param_in='header'
    )
    return http_client


def load_trs_client(service_id=None, http_client=None):
    """
    Return an API client for the selected workflow execution service.
    """
    if http_client is None:
        http_client = _init_http_client(service_id=service_id)
    return SwaggerClient.from_url(
        'https://raw.githubusercontent.com/ga4gh/tool-registry-service-schemas/develop/src/main/resources/swagger/ga4gh-tool-discovery.yaml',
        http_client=http_client
    ).GA4GH