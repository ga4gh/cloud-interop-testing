#!/usr/bin/env python
"""
Takes a given ID/URL for a workflow registered in a given TRS
implementation; prepare the workflow run request, including
retrieval and formatting of parameters, if not provided; post
the workflow run request to a given WES implementation;
monitor and report results of the workflow run.
"""
import logging
import sys
import time
import os
import datetime as dt
import re

from requests.exceptions import ConnectionError
from IPython.display import display, clear_output

from synorchestrator.config import wes_config, trs_config
from synorchestrator.config import eval_config as queue_config
from synorchestrator.util import get_json, ctime2datetime, convert_timedelta
from synorchestrator.wes.wrapper import WES
from synorchestrator.trs.client import TRSClient
from synorchestrator.eval import create_submission
from synorchestrator.eval import get_submission_bundle
from synorchestrator.eval import get_submissions
from synorchestrator.eval import update_submission
from synorchestrator.eval import update_submission_run
from synorchestrator.eval import submission_queue

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def no_queue_run(service, wf_name):
    """
    Put a workflow in the queue and immmediately run it.

    :param service:
    :param wf_name:
    :return:
    """
    # fetch workflow params from config file
    # 
    # synorchestrator.config.add_eval() can be used to add a workflow
    # to this file
    wf = eval_config()[wf_name]
    wf_data = {'wf': wf['workflow_url'],
               'jsonyaml': wf['workflow_jsonyaml'],
               'attachments': wf['workflow_attachments']}
    submission_id = create_submission(wes_id=service,
                                      submission_data=wf_data,
                                      wf_name=wf_name,
                                      wf_type=wf['workflow_type'])
    run_submission(service, submission_id)


def run_submission(queue_id, submission_id, wes_id=None):
    """
    For a single submission to a single evaluation queue, run
    the workflow in a single environment.
    """
    submission = get_submission_bundle(queue_id, submission_id)
    if submission['wes_id'] is not None:
        wes_id = submission['wes_id']

    logger.info(" Submitting to WES endpoint '{}':"
                " \n - submission ID: {}"
                .format(wes_id, submission_id))

    wes_instance = WES(wes_config()[wes_id])
    run_data = wes_instance.run_workflow(submission['data']['wf'],
                                         submission['data']['jsonyaml'],
                                         submission['data']['attachments'])
    run_data['start_time'] = dt.datetime.now().ctime()
    run_data['status'] = wes_instance.get_run_status(run_data['run_id'])
    update_submission(wes_id, submission_id, 'run', run_data)
    update_submission(wes_id, submission_id, 'status', 'SUBMITTED')
    return run_data


def run_queue(queue_id, wes_id=None):
    """
    Run all submissions in a queue in a single environment.
    """
    queue_handle = os.path.basename(queue_config()[queue_id]['workflow_id'])
    submission_log = {}
    for submission_id in get_submissions(queue_id, status='RECEIVED'):
        run_data = run_submission(queue_id, submission_id, wes_id)
        log_entry = {'queue_id': queue_id,
                     'job': run_data['type'],
                     'wes_id': wes_id,
                     'run_id': run_data['run_id'],
                     'status': run_data['status'],
                     'start_time': run_data['start_time']}
        submission_log.setdefault(queue_handle, {})[submission_id] = log_entry
    return submission_log


def run_next_queued(queue_id):
    """
    Run the next submission slated for a single evaluation queue.

    Return None if no submissions are queued.
    """
    queued_submissions = get_submissions(queue_id, status='RECEIVED')
    if not queued_submissions:
        return False
    for sub_id in sorted(queued_submissions):
        return run_submission(queue_id, sub_id)


def fetch_checker(trs, workflow_id):
    checker_workflow = trs.get_workflow_checker(workflow_id)

    checker_descriptor = trs.get_workflow_descriptor(
        id=checker_workflow['id'],
        version_id=workflow_config['version_id'],
        type=workflow_config['workflow_type']
    )

    checker_tests = trs.get_workflow_tests(
        id=checker_workflow['id'],
        version_id=workflow_config['version_id'],
        type=workflow_config['workflow_type']
    )
    return checker_descriptor, checker_tests


def build_checker_request(checker_descriptor, checker_tests):
    if (checker_descriptor['type'] == 'CWL' and
        re.search('run:', checker_descriptor['descriptor'])):
        checker_descriptor['descriptor'] = get_packed_cwl(checker_descriptor['url'])

    checker_request = build_wes_request(
        workflow_descriptor=checker_descriptor['descriptor'],
        workflow_params=checker_tests[0]['url'],
        workflow_type=checker_descriptor['type']
    )
    return checker_request


def check_queue(queue_id, wes_id):
    """
    Run checker workflow for an evaluation queue in a single
    environment.
    """
    wf_config = queue_config()[queue_id]
    wf_config['id'] = wf_config['workflow_id']
    logger.info("Preparing checker workflow run request for '{}' from  '{}''"
                .format(wf_config['id'], wf_config['trs_id']))
    
    trs_instance = TRSClient(**trs_config()[wf_config['trs_id']])

    checker_descriptor, checker_tests = fetch_checker(
        trs=trs_instance, 
        workflow_id=wf_config['id']
    )
    checker_request = build_checker_request(checker_descriptor, checker_tests)

    submission_id = create_submission(
        queue_id, checker_request, wes_id, type='checker'
    )
    return run_queue(queue_id)


def check_all(queue_wes_map):
    """
    Check workflows for multiple queues in multiple environments
    (cross product of queues, workflow service endpoints).
    """
    submission_logs = [check_queue(queue_id, wes_id)
                       for queue_id in queue_wes_map
                       for wes_id in queue_wes_map[queue_id]]
    return submission_logs


def run_all():
    """
    Run all jobs with the status: RECEIVED across all evaluation queues.
    Check the status of each submission per queue for status: COMPLETE
    before running the next queued submission.
    """
    submission_logs = [run_queue(queue_id) for queue_id in queue_config()]
    return submission_logs


def monitor_queue(queue_handle, submission_log):
    """
    Returns a dictionary of all of the jobs under a single wes service
    appropriate for displaying as a pandas dataframe.

    :param wf_service:
    :return:
    """
    current = dt.datetime.now()
    log_entry = submission_log[queue_handle]
    queue_status = {}
    for sub_id, sub_log in log_entry.items():
        wes_instance = WES(**wes_config()[sub_log['wes_id']])
        run_status = wes_instance.get_run_status(sub_log['run_id'])
        if run_status['state'] in ['QUEUED', 'INITIALIZING', 'RUNNING']:
            etime = convert_timedelta(
                current - ctime2datetime(sub_log['start_time'])
            )
        elif 'elapsed_time' not in sub_log:
            etime = 0
        else:
            etime = sub_log['elapsed_time']
        queue_status.setdefault(queue_handle, {})[sub_id] = {
            'queue_id': sub_log['queue_id'],
            'job': sub_log['job'],
            'wes_id': sub_log['wes_id'],
            'run_id': run_status['run_id'],
            'status': run_status['state'],
            'start_time': sub_log['start_time'],
            'elapsed_time': etime
        }
    return queue_status


def monitor(submission_logs):
    """
    Monitor progress of workflow jobs.
    """
    import pandas as pd
    pd.set_option('display.width', 100)

    statuses = []

    for sub_log in submission_logs:
        queue_handle, submission_log = sub_log.items()[0]
        statuses.append(monitor_queue(queue_handle, submission_log))

    status_tracker = pd.DataFrame.from_dict(
        {(i, j): status[i][j]
            for status in statuses
            for i in status.keys()
            for j in status[i].keys()},
        orient='index')

    clear_output(wait=True)
    os.system('clear')
    display(status_tracker)
    sys.stdout.flush()
    if any(status_tracker['status']
           .isin(['QUEUED', 'INITIALIZING', 'RUNNING'])):
        time.sleep(1)
        monitor(statuses)
    else:
        print("Done")
        return statuses
