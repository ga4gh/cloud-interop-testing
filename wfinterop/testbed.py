#!/usr/bin/env python
"""
"""
import os
import logging
import urllib
import re
import time

from itertools import combinations_with_replacement
from requests.exceptions import ConnectionError

from wfinterop.config import add_queue
from wfinterop.config import queue_config
from wfinterop.trs import TRS
from wfinterop.wes import WES
from wfinterop.queue import create_submission
from wfinterop.orchestrator import run_queue, run_submission, monitor_queue
from wfinterop.util import get_json, save_json

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


testbed_log = os.path.join(os.path.dirname(__file__),
                           'testbed_log.json')


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


def check_workflow(queue_id, wes_id, opts=None, force=False):
    """
    Run checker workflow in a single environment.
    """
    if not isinstance(opts, list):
        opts = [opts]
    wf_config = queue_config()[queue_id]

    if wes_id in wf_config.get('wes_verified', []) and not force:
        logger.info("Workflow for '{}' already verified on '{}'"
                    .format(queue_id, wes_id))
        return
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

    testbed_status = get_json(testbed_log)
    for opt in opts:
        if 'run_id' in opt:
            opt.pop('run_id')
        submission_id = create_submission(queue_id=checker_queue_id,
                                          submission_data=checker_job['url'],
                                          wes_id=wes_id)
        logger.info("Created submission '{}' for queue '{}'; running in '{}'"
                    "with options: {}"
                    .format(submission_id, checker_queue_id, wes_id, opt))
        testbed_status.setdefault(checker_queue_id, {}).setdefault(wes_id, {})[submission_id] = opt
        save_json(testbed_log, testbed_status)
        run_log = run_submission(checker_queue_id, submission_id, opts=opt)
        testbed_status[checker_queue_id][wes_id][submission_id]['run_id'] = run_log['run_id']
        save_json(testbed_log, testbed_status)
    
    return testbed_status


def get_opts(permute=False):
    opts = [
        "attach_descriptor",
        "resolve_params" ,
        "attach_imports"
    ]
    n = len(opts)
    if not permute:
        return [dict(zip(opts, [False]*n))]
    else:
        states = set(combinations_with_replacement([True, False]*(n-1), n))
        return [dict(zip(opts, state)) for state in states]


def check_all(workflow_wes_map, permute_opts=False, force=False):
    """
    Check workflows for multiple workflows in multiple environments
    (cross product of workflows, workflow service endpoints).
    """
    opts_list = get_opts(permute_opts)
    testbed_status = [check_workflow(workflow_id, 
                                     wes_id, 
                                     opts=opts_list,
                                     force=force)
                      for workflow_id in workflow_wes_map
                      for wes_id in workflow_wes_map[workflow_id]][-1]
    logger.info("tbs: {}".format(testbed_status))
    while True:
        terminal_statuses = ['COMPLETE', 'CANCELED', 'EXECUTOR_ERROR']
        testbed_statuses = [sub_log['status'] 
                            if 'status' in sub_log else 'PENDING'
                            for queue_log in testbed_status.values()
                            for wes_log in queue_log.values()
                            for sub_log in wes_log.values()]
        if (len(testbed_statuses) and 
            all([status in terminal_statuses 
                 for status in testbed_statuses])):
            break

        for queue_id in testbed_status:
            queue_logs = monitor_queue(queue_id)
            queue_statuses = map(lambda x: x['status'], queue_logs.values())
            sub_statuses = dict(zip(queue_logs.keys(), queue_statuses))
            for wes_id in testbed_status[queue_id]:
                for sub_id in testbed_status[queue_id][wes_id]:
                    testbed_status[queue_id][wes_id][sub_id]['status'] = sub_statuses[sub_id]
        save_json(testbed_log, testbed_status)
        time.sleep(2)
    
    return testbed_status

# testbed_dict = {queue_id: testbed_status[queue_id][wes_id][sub_id] 
#                 for queue_id in testbed_status 
#                 for wes_id in testbed_status[queue_id] 
#                 for sub_id in testbed_status[queue_id][wes_id]}
# pd.DataFrame.from_dict(testbed_dict, orient='index')