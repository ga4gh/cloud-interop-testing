#!/usr/bin/env python
"""
Load API client for a Tool Registry Service (DRS) endpoint based
either on the GA4GH specification or an existing client library.
"""
import logging

from bravado.requests_client import RequestsClient

from ga4ghtest.core.config import drs_config
from .client import DRSClient

logger = logging.getLogger(__name__)


def _get_drs_opts(service_id):
    """
    Look up stored parameters for tool registry services.
    """
    return drs_config()[service_id]


def _init_http_client(service_id=None, opts=None):
    """
    Initialize and configure HTTP requests client for selected service.
    """
    if service_id:
        opts = _get_drs_opts(service_id)

    http_client = RequestsClient()

    http_client.set_api_key(host=opts['host'],
                            api_key=opts['auth'],
                            param_in='header')
    return http_client


class DRSInterface:
    def GetServiceInfo(self):
        raise NotImplementedError

    def GetBundle(self, bundle_id):
        raise NotImplementedError

    def GetObject(self, object_id):
        raise NotImplementedError

    def GetAccessURL(self, object_id):
        raise NotImplementedError

    def DownloadFile(self, object_id):
        raise NotImplementedError

class DRSAdapter(DRSInterface):
    """
    Adapter class for DRS client functionality.

    Args:
        drs_client: ...
    """
    def __init__(self, drs_client):
        self.drs_client = drs_client

    def GetServiceInfo(self):
        return self.drs_client.get_service_info()

    def GetBundle(self, bundle_id):
        return self.drs_client.getBundle(bundle_id)

    def GetObject(self, object_id):
        raise self.drs_client.getObject(object_id)

    def GetAccessURL(self, object_id):
        return self.drs_client.getAccessURL(object_id)

    def DownloadFile(self, object_id, destPath):
        return self.drs_client.downloadFile(object_id, destPath)

def load_drs_client(service_id, http_client=None):
    """Return an API client for the selected workflow execution service."""
    drs_client = DRSClient(service=_get_drs_opts(service_id))
    return DRSAdapter(drs_client)
