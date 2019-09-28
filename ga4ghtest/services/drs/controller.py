#!/usr/bin/env python
"""
Wrapper class around Tool Registry Service (DRS) API client to
provide consistent Pythonic interface.
"""
import logging
import urllib.parse as urlparse
import re

from ga4ghtest.services.drs.api import load_drs_client
from ga4ghtest.util import response_handler

logger = logging.getLogger(__name__)

class DRSService(object):
    """
    Build a :class:`DRS` instance for interacting with a server via
    the GA4GH Tool Registry Service RESTful API.

    Args:
        drs_id (str): ...
        api_client (str): ...
    """
    def __init__(self, drs_id, api_client=None):
        if api_client is None:
            api_client = load_drs_client(service_id=drs_id)
        self.api_client = api_client

    def get_serviceInfo(self):
        """
        Get information about this implementation.
        """
        res = self.api_client.GetServiceInfo()
        return response_handler(res)

    def get_bundle(self, bundle_id, api_client=None):
        """
        Returns bundle metadata, and a list of ids that can be used to fetch bundle contents.

        Args:
            bundle_id (str): ...
        """
        res = self.api_client.GetBundle(bundle_id)
        return response_handler(res)

    def get_object(self, object_id, api_client=None):
        """
        Returns object metadata, and a list of access methods that can be used to fetch object bytes.

        Args:
            object_id (str): ...
        """

        res = self.api_client.GetObject(object_id)
        return response_handler(res)

    def get_access_url(self, object_id, api_client=None):
        """
        Returns a URL that can be used to fetch the object bytes.


        This method only needs to be called when using an `AccessMethod` that contains an `access_id`
        (e.g., for servers that use signed URLs for fetching object bytes).
        """
        res = self.api_client.GetObject(object_id)
        return response_handler(res)

    def download_file(self, object_id, destPath, api_client=None):
        """
        Download the DRS Object to local filesystem
        """

        self.api_client.DownloadFile(object_id, destPath)