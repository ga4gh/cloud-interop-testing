import logging
import urllib
import re

from synorchestrator.trs.client import load_trs_client

logger = logging.getLogger(__name__)


def _format_workflow_id(id):
    """
    Add workflow prefix to and quote a tool ID.
    """
    id = urllib.unquote(id)
    if not re.search('^#workflow', id):
        return urllib.quote_plus('#workflow/{}'.format(id))
    else:
        return urllib.quote_plus(id)


class TRS(object):
    """
    Build a :class:`TRS` instance for interacting with a server via
    the GA4GH Tool Registry Service RESTful API.
    """
    def __init__(self, trs_id, api_client=None):
        if api_client is None:
            api_client = load_trs_client()
        self.api_client = api_client

    def get_metadata(self):
        """
        Return some metadata that is useful for describing the service.
        """
        res = self.api_client.metadataGet()
        return res.response().result

    def get_workflow(self, id):
        """
        Return one specific tool of class "workflow" (which has
        ToolVersions nested inside it).
        """
        id = _format_workflow_id(id)
        res = self.api_client.toolsIdGet(id=id)
        return _response_handler(res)

    # def get_workflow_checker(self, id):
    #     """
    #     Return entry for the specified workflow's "checker workflow."
    #     """
    #     checker_url = urllib.unquote(self.get_workflow(id=id)['checker_url'])
    #     checker_id = re.sub('^.*#workflow/', '', checker_url)
    #     logger.info("found checker workflow: {}".format(checker_id))
    #     return self.get_workflow(id=checker_id)

    def get_workflow_versions(self, id):
        """
        Return all versions of the specified workflow.
        """
        id = _format_workflow_id(id=id)
        res = self.api_client.toolsIdVersionsGet(id=id)
        return _response_handler(res)

    def get_workflow_descriptor(self, id, version_id, type):
        """
        Return the descriptor for the specified workflow (examples
        include CWL, WDL, or Nextflow documents).
        """
        # toolsIdVersionsVersionIdTypeDescriptorGet
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
        # toolsIdVersionsVersionIdTypeTestsGet
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
        # toolsIdVersionsVersionIdTypeFilesGet
        fileid = _format_workflow_id(fileid)
        endpoint = 'tools/{}/versions/{}/{}/files'.format(fileid, version_id, filetype)
        return _get_endpoint(self, endpoint)

    def post_verification(self, id, version_id, type, relative_path, requests):
        """
        Annotate test JSON with information on whether it ran successfully on particular platforms plus metadata
        """
        id = _format_workflow_id(id)
        endpoint ='extended/{}/versions/{}/{}/tests/{}'.format(
            id, version_id, type, relative_path
        )
        return _post_to_endpoint(self, endpoint, requests)


def _response_handler(response):
    try:
        return response.response().result
    except:
        return response