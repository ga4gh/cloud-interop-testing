#!/usr/bin/env python
"""
"""
import os
import logging
import urllib
import re
import time
import shutil

from IPython.display import display, clear_output
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
if not os.path.exists(testbed_log):
    save_json(testbed_log, {})


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
    if opts is None:
        opts = get_opts()
    if not isinstance(opts, list):
        opts = [opts]
    wf_config = queue_config()[queue_id]
    testbed_status = get_json(testbed_log)

    if wes_id in wf_config.get('wes_verified', []) and not force:
        logger.info("Workflow for '{}' already verified on '{}'"
                    .format(queue_id, wes_id))
        return testbed_status
    logger.info("Preparing checker workflow run request for '{}' from  '{}'"
                .format(wf_config['workflow_id'], wf_config['trs_id']))
    trs_instance = TRS(wf_config['trs_id'])
    checker_queue_id = '{}_checker'.format(queue_id)
    if checker_queue_id in queue_config():
        checker_id = queue_config()[checker_queue_id]['workflow_id']
    else:
        checker_id = get_checker_id(trs_instance, wf_config['workflow_id'])
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
        logger.info("Requesting new workflow run for '{}' in '{}'"
                    .format(checker_queue_id, wes_id))
        run_log = run_submission(checker_queue_id, submission_id, opts=opt)
        testbed_status[checker_queue_id][wes_id][submission_id]['run_id'] = run_log['run_id']
        save_json(testbed_log, testbed_status)
    
    return testbed_status


def get_opts(permute=False):
    opts = [
        "attach_descriptor",
        "resolve_params" ,
        "attach_imports",
        "pack_descriptor"
    ]
    n = len(opts)
    if not permute:
        return [dict(zip(opts, [False]*n))]
    else:
        states = set(combinations_with_replacement([True, False]*(n-1), n))
        return filter(lambda x: not (x['pack_descriptor'] 
                                     and (x['attach_imports'] 
                                          or not x['attach_descriptor'])),
                      [dict(zip(opts, state)) for state in states])


def collect_logs(testbed_status):
    for queue_id in testbed_status:
        for wes_id in testbed_status[queue_id]:
            log_dir = os.path.join('logs', queue_id, wes_id)
            if not os.path.exists(log_dir):
                os.makedirs(log_dir)
            for sub_id in testbed_status[queue_id][wes_id]:
                run_id = testbed_status[queue_id][wes_id][sub_id]['run_id']
                log_src = os.path.join('logs', '{}.request'.format(run_id))
                log_dest = os.path.join(log_dir, os.path.basename(log_src))
                shutil.move(log_src, log_dest)


def monitor_testbed():
    testbed_status = get_json(testbed_log)
    while True:
        terminal_statuses = ['COMPLETE', 'CANCELED', 'EXECUTOR_ERROR',
                             'SYSTEM_ERROR', 'FAILED', 'Failed']
        queue_statuses = [(queue_id, sub_log['status'])
                          if 'status' in sub_log else (queue_id, 'PENDING')
                          for queue_id in testbed_status
                          for wes_log in testbed_status[queue_id].values()
                          for sub_log in wes_log.values()]
        testbed_statuses = filter(lambda x: x[1] not in terminal_statuses, queue_statuses)
        if not len(testbed_statuses): 
            collect_logs(testbed_status)
            break

        for queue_id in set([x[0] for x in testbed_statuses]):
            logger.info("Checking status of runs in queue '{}'"
                        .format(queue_id))
            queue_logs = monitor_queue(queue_id)
            queue_statuses = map(lambda x: x['status'], queue_logs.values())
            live_statuses = [s for s in queue_statuses if s not in terminal_statuses]
            logger.info("... {} jobs still remaining".format(len(live_statuses)))
            sub_statuses = dict(zip(queue_logs.keys(), queue_statuses))
            for wes_id in testbed_status[queue_id]:
                logger.debug("Recording statuses for queue '{}'\n > '{}'"
                             .format(queue_id, wes_id))
                for sub_id in testbed_status[queue_id][wes_id]:
                    testbed_status[queue_id][wes_id][sub_id]['status'] = sub_statuses[sub_id]
        save_json(testbed_log, testbed_status)
        time.sleep(2)
    return testbed_status


def check_all(testbed_plan, permute_opts=False, force=False):
    """
    Check workflows for multiple workflows in multiple environments
    (cross product of workflows, workflow service endpoints).
    """
    opts_list = get_opts(permute_opts)
    testbed_status = [check_workflow(workflow_id, 
                                     wes_id, 
                                     opts=opts_list,
                                     force=force)
                      for workflow_id in testbed_plan
                      for wes_id in testbed_plan[workflow_id]][-1]
    testbed_status = monitor_testbed()
    return testbed_status


def testbed_report():
    import pandas as pd
    pd.set_option('display.width', 1000)
    pd.set_option('display.max_columns', 10)
    pd.set_option('display.max_rows', 250)
    pd.set_option('display.expand_frame_repr', False)

    testbed_status = get_json(testbed_log)
    testbed_dict = {}
    for queue_id in testbed_status:
        for wes_id in testbed_status[queue_id]:
            for sub_id in testbed_status[queue_id][wes_id]:
                testbed_record = testbed_status[queue_id][wes_id][sub_id]
                testbed_record.update({'wes_id': wes_id})
                testbed_dict[(queue_id, sub_id)] = testbed_record
    status_report = pd.DataFrame.from_dict(testbed_dict, orient='index')

    display(status_report)
    return status_report
