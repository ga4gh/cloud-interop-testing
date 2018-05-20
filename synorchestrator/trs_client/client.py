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


def _format_workflow_id(id):
    """
    Add workflow prefix to and quote a tool ID.
    """
    if not re.search('^#workflow', id):
        return urllib.quote_plus('#workflow/{}'.format(id))
    else:
        return urllib.quote_plus(id)


class TRSClient(object):
    """
    Build a :class:`SwaggerClient` from a url to the Swagger
    specification for the GA4GH Tool Registry Service RESTful API.
    """
    def __init__(self, host, auth=None, proto='http'):
        self.base_url = '{}://{}/api/ga4gh/v2'.format(proto, host)
        self.headers = {'Authorization': auth}


    def get_workflow(self, id):
        """
        Return one specific tool of class "workflow" (which has
        ToolVersions nested inside it).
        """
        id = _format_workflow_id(id)
        endpoint = 'tools/{}'.format(id)
        logging.debug("retrieving workflow entry from {}".format(endpoint))
        return _get_endpoint(self, endpoint)


    def get_workflow_checker(self, id):
        """
        Return URL for the specified workflow's "checker workflow."
        """
        checker_url = urllib.unquote(self.get_workflow(id)['checker_url'])
        checker_id = re.sub('^.*#workflow/', '', checker_url)
        logger.debug("found checker workflow: {}".format(checker_id))
        return self.get_workflow(checker_id)


    def get_workflow_versions(self, id):
        """
        Return all versions of the specified workflow.
        """
        id = _format_workflow_id(id)
        endpoint = 'tools/{}/versions'.format(id)
        return _get_endpoint(self, endpoint)


    def get_workflow_descriptor(self, id, version_id, type):
        """
        Return the descriptor for the specified workflow (examples
        include CWL, WDL, or Nextflow documents).
        """
        id = _format_workflow_id(id)
        endpoint = 'tools/{}/versions/{}/{}/descriptor'.format(
            id, version_id, type
        )
        return _get_endpoint(self, endpoint)


    def get_workflow_tests(self, id, version_id, type):
        """
        Return a list of test JSONs (these allow you to execute the
        workflow successfully) suitable for use with this descriptor
        type.
        """
        id = _format_workflow_id(id)
        endpoint = 'tools/{}/versions/{}/{}/tests'.format(
            id, version_id, type
        )
        return _get_endpoint(self, endpoint)
