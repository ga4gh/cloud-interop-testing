#!/usr/bin/env python
"""
"""
import logging
import urllib
import re

from requests.exceptions import ConnectionError

from wfinterop.config import add_queue
from wfinterop.config import queue_config
from wfinterop.trs import TRS
from wfinterop.wes import WES
from wfinterop.queue import create_submission
from wfinterop.orchestrator import run_queue

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def poll_services():
    """
    Check connection to services in testbed.
    """
    trs_opts = []
    wes_opts = []
    for wf_config in queue_config().values():
        trs_opts.append(wf_config['trs_id'])
        wes_opts += wf_config['wes_opts']

    trs_status = {}
    for trs_id in list(set(trs_opts)):
        trs_instance = TRS(trs_id=trs_id)
        trs_status[trs_id] = True
        try:
            trs_instance.get_metadata()
        except ConnectionError:
            trs_status[trs_id] = False

    wes_status = {}
    for wes_id in list(set(wes_opts)):
        wes_instance = WES(wes_id=wes_id)
        wes_status[wes_id] = True
        try:
            wes_instance.get_service_info()
        except ConnectionError:
            wes_status[wes_id] = False

    return {'toolregistries': trs_status, 'workflowservices': wes_status}


def get_checker_id(trs, workflow_id):
    """
    Return entry for the specified workflow's "checker workflow."
    """
    target_workflow = trs.get_workflow(id=workflow_id)
    checker_url = urllib.unquote(target_workflow['checker_url'])
    checker_id = re.sub('^.*#workflow/', '', checker_url)
    logger.info("found checker workflow: {}".format(checker_id))
    return checker_id


def check_workflow(queue_id, wes_id):
    """
    Run checker workflow in a single environment.
    """
    wf_config = queue_config()[queue_id]
    logger.info("Preparing checker workflow run request for '{}' from  '{}'"
                .format(wf_config['workflow_id'], wf_config['trs_id']))

    trs_instance = TRS(wf_config['trs_id'])
    checker_id = get_checker_id(trs_instance, wf_config['workflow_id'])

    checker_queue_id = '{}_checker'.format(queue_id)
    add_queue(queue_id=checker_queue_id,
              wf_type=wf_config['workflow_type'],
              trs_id=wf_config['trs_id'],
              wf_id=checker_id,
              version_id=wf_config['version_id'],
              wes_default=wf_config['wes_default'],
              wes_opts=wf_config['wes_opts'],
              target_queue=queue_id)

    checker_tests = trs_instance.get_workflow_tests(
        id=checker_id,
        version_id=wf_config['version_id'],
        type=wf_config['workflow_type']
    )
    checker_job = checker_tests[0]

    submission_id = create_submission(queue_id=checker_queue_id,
                                      submission_data=checker_job['url'],
                                      wes_id=wes_id)
    logger.info("Created submission '{}' for queue '{}'; running in '{}'"
                .format(submission_id, checker_queue_id, wes_id))
    return run_queue(checker_queue_id)


def check_all(workflow_wes_map):
    """
    Check workflows for multiple workflows in multiple environments
    (cross product of workflows, workflow service endpoints).
    """
    submission_logs = [check_workflow(workflow_id, wes_id)
                       for workflow_id in workflow_wes_map
                       for wes_id in workflow_wes_map[workflow_id]]
    return submission_logs
