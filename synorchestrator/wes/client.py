import logging
import requests
import urllib
import re

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def _get_endpoint(client, endpoint):
    """
    Execute a generic API 'GET' request.
    """
    res = requests.get(
        '{}/{}'.format(client.base_url, endpoint),
        headers=client.headers
    )
    # TODO: add some exception handling for different responses
    return res.json()


def _post_to_endpoint(client, endpoint, request):
    """
    Execute a generic API 'POST' request.
    """
    res = requests.post(
        '{}/{}'.format(client.base_url, endpoint),
        headers=client.headers,
        json=request
    )
    # TODO: add some exception handling for different responses
    return res.json()


class WESClient(object):
    """
    Build a :class:`WESClient` for interacting with a server via
    the GA4GH Worflow Execution Service RESTful API.
    """
    def __init__(self, host, auth=None, auth_type=None, proto='http',
                 base_path='ga4gh/wes/v1'):
        self.base_url = '{}://{}/{}'.format(proto, host, base_path)
        auth_headers = {'token': 'Authorization',
                        'api_key': 'X-API-KEY',
                        None: ''}
        self.headers = {auth_headers[auth_type]: auth}


    def get_service_info(self):
        """
        Get information about Workflow Execution Service.
        """
        endpoint = 'service-info'
        return _get_endpoint(self, endpoint)


    def list_workflow_runs(self):
        """
        List all the workflow runs in order of oldest to newest.
        """
        endpoint = 'workflows'
        return _get_endpoint(self, endpoint)


    def run_workflow(self, request):
        """
        Create a new workflow run and retrieve its tracking ID
        to monitor its progress.
        """
        endpoint = 'workflows'
        return _post_to_endpoint(self, endpoint, request)


    def get_workflow_run(self, id):
        """
        Get detailed info about a workflow run.
        """
        endpoint = 'workflows/{}'.format(id)
        return _get_endpoint(self, endpoint)


    def get_workflow_run_status(self, id):
        """
        Get quick status info about a workflow run.
        """
        endpoint = 'workflows/{}/status'.format(id)
        return _get_endpoint(self, endpoint)
