import logging

from synorchestrator.wes.client import load_wes_client
from synorchestrator.util import response_handler

logger = logging.getLogger(__name__)


class WES(object):
    """
    Build a :class:`WES` instance for interacting with a server via
    the GA4GH Worflow Execution Service RESTful API.
    """
    def __init__(self, wes_id, api_client=None):
        if api_client is None:
            api_client = load_wes_client(service_id=wes_id)
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

    def run_workflow(self, request):
        """
        Create a new workflow run and retrieve its tracking ID
        to monitor its progress.
        """
        res = self.api_client.RunWorkflow(request)
        return response_handler(res)

    def cancel_run(self, id):
        """
        Cancel a running workflow.
        """
        res = self.api_client.CancelRun(id)
        return response_handler(res)

    def get_run(self, id):
        """
        Get detailed info about a workflow run.
        """
        res = self.api_client.GetRunLog(id)
        return response_handler(res)

    def get_run_status(self, id):
        """
        Get quick status info about a workflow run.
        """
        res = self.api_client.GetRunStatus(id)
        return response_handler(res)
