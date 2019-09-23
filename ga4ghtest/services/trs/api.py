#!/usr/bin/env python
"""
Load API client for a Tool Registry Service (TRS) endpoint based
either on the GA4GH specification or an existing client library.
"""
import logging

from bravado.requests_client import RequestsClient

from ga4ghtest.core.config import trs_config
from .client import TRSClient

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
    if service_id:
        opts = _get_trs_opts(service_id)

    http_client = RequestsClient()

    http_client.set_api_key(host=opts['host'],
                            api_key=opts['auth'],
                            param_in='header')
    return http_client


class TRSInterface:
    def toolsGet(self):
        raise NotImplementedError

    def toolTypesGet(self):
        raise NotImplementedError

    def toolsIdGet(self, tool_id):
        raise NotImplementedError

    def toolsIdVersionGet(self, tool_id, tool_version):
        raise NotImplementedError

    def toolsIdVersionsGet(self, tool_id):
        raise NotImplementedError

    def toolsIdVersionsVersionIdTypeDescriptorGet(self, tool_id, tool_version, descriptor_type):
        raise NotImplementedError

    def toolsIdVersionsVersionIdTypeDescriptorRelativePathGet(self, tool_id, tool_version, descriptor_type, rel_path):
        raise NotImplementedError

    def toolsIdVersionsVersionIdTypeTestsGet(self, tool_id, tool_version, descriptor_type, rel_path):
        raise NotImplementedError

    def toolsIdVersionsVersionIdTypeFilesGet(self, tool_id, tool_version, descriptor_type):
        raise NotImplementedError

    def toolsIdVersionsContainerGet(self, tool_id, tool_version):
        raise NotImplementedError


class TRSAdapter(TRSInterface):
    """
    Adapter class for TRS client functionality.

    Args:
        trs_client: ...
    """
    def __init__(self, trs_client):
        self.trs_client = trs_client

    def toolsGet(self):
        return self.trs_client.get_tools()

    def toolTypesGet(self):
        raise self.trs_client.get_tool_types()

    def toolsIdGet(self, tool_id):
        return self.trs_client.get_tool(tool_id)

    def toolsIdVersionGet(self, tool_id, tool_version):
        return self.trs_client.get_tool_version(tool_id, tool_version)

    def toolsIdVersionsGet(self, tool_id):
        return self.trs_client.get_tool_versions(tool_id)

    def toolsIdVersionsVersionIdTypeDescriptorGet(self, tool_id, tool_version, descriptor_type):
        return self.trs_client.get_tool_descriptor(tool_id, tool_version, descriptor_type)

    def toolsIdVersionsVersionIdTypeDescriptorRelativePathGet(self, tool_id, tool_version, descriptor_type, rel_path):
        return self.trs_client.get_relative_tool_descriptor(tool_id, tool_version, descriptor_type, rel_path)

    def toolsIdVersionsVersionIdTypeTestsGet(self, tool_id, tool_version, descriptor_type, rel_path):
        return self.trs_client.get_tool_tests(tool_id, tool_version, descriptor_type, rel_path)

    def toolsIdVersionsVersionIdTypeFilesGet(self, tool_id, tool_version, descriptor_type):
        return self.trs_client.get_tools_with_relative_path(tool_id, tool_version, descriptor_type)

    def toolsIdVersionsContainerGet(self, tool_id, tool_version):
        return self.trs_client.get_tool_container_specs(tool_id, tool_version)


def load_trs_client(service_id, http_client=None):
    """Return an API client for the selected workflow execution service."""
    trs_client = TRSClient(service=_get_trs_opts(service_id))
    return TRSAdapter(trs_client)
