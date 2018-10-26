"""
"""
import logging
import urllib
import re

from wfinterop.trs.client import load_trs_client
from wfinterop.util import response_handler

logger = logging.getLogger(__name__)


def _format_workflow_id(id):
    """
    Add workflow prefix to and quote a tool ID.

    :param str id:
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

    :param str trs_id:
    :param api_client:
    """
    def __init__(self, trs_id, api_client=None):
        if api_client is None:
            api_client = load_trs_client(service_id=trs_id)
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

        :param str id:
        """
        id = _format_workflow_id(id)
        res = self.api_client.toolsIdGet(id=id)
        return response_handler(res)

    def get_workflow_versions(self, id):
        """
        Return all versions of the specified workflow.

        :param str id:
        """
        id = _format_workflow_id(id=id)
        res = self.api_client.toolsIdVersionsGet(id=id)
        return response_handler(res)

    def get_workflow_descriptor(self, id, version_id, type):
        """
        Return the descriptor for the specified workflow (examples
        include CWL, WDL, or Nextflow documents).

        :param str id:
        :param str version_id:
        :param str type:
        """
        id = _format_workflow_id(id)
        res = self.api_client.toolsIdVersionsVersionIdTypeDescriptorGet(
            id=id,
            version_id=version_id,
            type=type
        )
        return response_handler(res)

    def get_workflow_descriptor_relative(self,
                                         id,
                                         version_id,
                                         type,
                                         relative_path):
        """
        Return an additional tool descriptor file relative to the main file.

        :param str id:
        :param str version_id:
        :param str type:
        :param str relative_path:
        """
        id = _format_workflow_id(id)
        res = self.api_client.toolsIdVersionsVersionIdTypeDescriptorRelativePathGet(
            id=id,
            version_id=version_id,
            type=type,
            relative_path=relative_path
        )
        return response_handler(res)

    def get_workflow_tests(self, id, version_id, type):
        """
        Return a list of test JSONs (these allow you to execute the
        workflow successfully) suitable for use with this descriptor type.

        :param str id:
        :param str version_id:
        :param str type:
        """
        id = _format_workflow_id(id)
        res = self.api_client.toolsIdVersionsVersionIdTypeTestsGet(
            id=id,
            version_id=version_id,
            type=type
        )
        return response_handler(res)

    def get_workflow_files(self, id, version_id, type):
        """
        Return a list of files associated with the workflow based
        on file type.

        :param str id:
        :param str version_id:
        :param str type:
        """
        id = _format_workflow_id(id)
        res = self.api_client.toolsIdVersionsVersionIdTypeFilesGet(
            id=id,
            version_id=version_id,
            type=type
        )
        return response_handler(res)
