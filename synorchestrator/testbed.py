#!/usr/bin/env python
"""
"""
import logging
import urllib
import re

from synorchestrator.config import eval_config as queue_config
from synorchestrator.config import trs_config

from synorchestrator.trs.wrapper import TRS
from synorchestrator.eval import create_submission
from synorchestrator.orchestrator import run_queue

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def testbed_config():
    pass


def create_queue():
    pass


def get_checker_id(trs, workflow_id):
    """
    Return entry for the specified workflow's "checker workflow."
    """
    target_workflow = trs.get_workflow(id=workflow_id)
    checker_url = urllib.unquote(target_workflow['checker_url'])
    checker_id = re.sub('^.*#workflow/', '', checker_url)
    logger.info("found checker workflow: {}".format(checker_id))
    return checker_id


def check_workflow(workflow_id, wes_id):
    """
    Run checker workflow in a single environment.
    """
    wf_config = testbed_config()[workflow_id]
    logger.info("Preparing checker workflow run request for '{}' from  '{}''"
                .format(workflow_id, wf_config['trs_id']))
    
    trs_instance = TRS(**trs_config()[wf_config['trs_id']])
    checker_id = get_checker_id(trs_instance, workflow_id)
    
    queue_id = create_queue(workflow={'trs_id': wf_config['trs_id'],
                                      'id': checker_id,  
                                      'version_id': wf_config['version_id'],
                                      'type': wf_config['type']})

    checker_job = trs_instance.get_workflow_tests(id=checker_id,
                                         version_id=wf_config['version_id'],
                                         type=wf_config['type'])[0]

    submission_id = create_submission(queue_id=queue_id, 
                                      submission_data=checker_job, 
                                      wes_id=wes_id, 
                                      type='checker')
    return run_queue(queue_id)


def check_all(workflow_wes_map):
    """
    Check workflows for multiple workflows in multiple environments
    (cross product of workflows, workflow service endpoints).
    """
    submission_logs = [check_workflow(workflow_id, wes_id)
                       for workflow_id in workflow_wes_map
                       for wes_id in workflow_wes_map[workflow_id]]
    return submission_logs


# def post_verification(self, id, version_id, type, relative_path, requests):
#     """
#     Annotate test JSON with information on whether it ran successfully on particular platforms plus metadata
#     """
#     id = _format_workflow_id(id)
#     endpoint ='extended/{}/versions/{}/{}/tests/{}'.format(
#         id, version_id, type, relative_path
#     )
#     return _post_to_endpoint(self, endpoint, requests)