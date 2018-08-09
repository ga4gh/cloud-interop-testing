import logging
import os
import requests
import urllib
import re

logger = logging.getLogger(__name__)


def _get_endpoint(client, endpoint):
    """
    Execute a generic API 'GET' request.
    """
    res = requests.get('{}/{}'.format(client.base_url, endpoint), headers=client.headers)
    # TODO: add some exception handling for different responses
    return res.json()


def _format_workflow_id(id):
    """
    Add workflow prefix to and quote a tool ID.
    """
    id = urllib.unquote(id)
    if not re.search('^#workflow', id):
        return urllib.quote_plus('#workflow/{}'.format(id))
    else:
        return urllib.quote_plus(id)


class TRSClient(object):
    """
    Build a :class:`TRSClient` for interacting with a server via
    the GA4GH Tool Registry Service RESTful API.
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
        logging.info("retrieving workflow entry from {}".format(endpoint))
        return _get_endpoint(self, endpoint)

    def get_workflow_checker(self, id):
        """
        Return entry for the specified workflow's "checker workflow."
        """
        checker_url = urllib.unquote(self.get_workflow(id)['checker_url'])
        checker_id = re.sub('^.*#workflow/', '', checker_url)
        logger.info("found checker workflow: {}".format(checker_id))
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
        logger.info("getting descriptor from {}".format(endpoint))
        return _get_endpoint(self, endpoint)

    def get_workflow_tests(self, fileid, version_id, filetype, fix_url=True):
        """
        Return a list of test JSONs (these allow you to execute the
        workflow successfully) suitable for use with this descriptor type.
        """
        fileid = _format_workflow_id(fileid)
        endpoint = 'tools/{}/versions/{}/{}/tests'.format(fileid, version_id, filetype)
        tests = _get_endpoint(self, endpoint)
        if fix_url:
            descriptor = self.get_workflow_descriptor(fileid, version_id, filetype)
            for test in tests:
                if test['url'].startswith('/'):
                    test['url'] = os.path.join(os.path.dirname(descriptor['url']), os.path.basename(tests[0]['url']))
        return tests

    def get_workflow_files(self, fileid, version_id, filetype):
        """
        Return a list of files associated with the workflow based
        on file type.
        """
        fileid = _format_workflow_id(fileid)
        endpoint = 'tools/{}/versions/{}/{}/files'.format(fileid, version_id, filetype)
        return _get_endpoint(self, endpoint)
