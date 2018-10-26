#!/usr/bin/env python
"""
Wrapper class around Workflow Execution Service (WES) API client to
provide consistent Pythonic interface.
"""
import logging
import requests

from wfinterop.wes.client import load_wes_client
from wfinterop.util import response_handler
from wfinterop.config import wes_config

logger = logging.getLogger(__name__)

wes_client = 'workflow-service'


class WES(object):
    """
    Build a :class:`WES` instance for interacting with a server via
    the GA4GH Worflow Execution Service RESTful API.

    Args:
        wes_id (str): ...
        api_client: ...
    """
    def __init__(self, wes_id, api_client=None):
        self.id = wes_id
        if api_client is None:
            api_client = load_wes_client(service_id=wes_id,
                                         client_library=wes_client)
        self.api_client = api_client

    def get_service_info(self):
        """
        Get information about Workflow Execution Service.
        """
        res = self.api_client.GetServiceInfo()
        return response_handler(res)

    def list_runs(self):
        """
        List all the workflow runs in order of oldest to newest.
        """
        res = self.api_client.ListRuns()
        return response_handler(res)

    def run_workflow(self, request, parts=None):
        """
        Create a new workflow run and retrieve its tracking ID
        to monitor its progress.

        Args:
            request (dict): ...
            parts (list): ...
        
        Returns:
            ...
        """
        res = self.api_client.RunWorkflow(request, parts)
        return response_handler(res)

    def cancel_run(self, id):
        """
        Cancel a running workflow.

        Args:
            id (str): ...

        Returns:
            ...
        """
        res = self.api_client.CancelRun(id)
        return response_handler(res)

    def get_run(self, id):
        """
        Get detailed info about a workflow run.

        Args:
            id (str): ...

        Returns:
            ...
        """
        res = self.api_client.GetRunLog(id)
        return response_handler(res)

    def get_run_status(self, id):
        """
        Get quick status info about a workflow run.

        Args:
            id (str): ...

        Returns:
            ...
        """
        res = self.api_client.GetRunStatus(id)
        return response_handler(res)

    def get_run_stderr(self, id):
        """
        Get stderr from workflow run log.

        Args:
            id (str): ...

        Returns:
            ...
        """
        stderr_url = self.get_run(id)['run_log']['stderr']
        auth = wes_config()[self.id]['auth']
        res = requests.get(stderr_url, headers=auth)
        return res.text

    def get_run_stdout(self, id):
        """
        Get stdout from workflow run log.

        Args:
            id (str): ...

        Returns:
            ...
        """
        stdout_url = self.get_run(id)['run_log']['stdout']
        auth = wes_config()[self.id]['auth']
        res = requests.get(stdout_url, headers=auth)
        return res.text
