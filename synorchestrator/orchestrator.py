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

from StringIO import StringIO
from requests.exceptions import ConnectionError
from IPython.display import display, clear_output

from synorchestrator.config import queue_config
from synorchestrator.util import get_json, ctime2datetime, convert_timedelta
from synorchestrator.wes.wrapper import WES
from trs2wes import fetch_queue_workflow
from synorchestrator.eval import get_submission_bundle
from synorchestrator.eval import get_submissions
from synorchestrator.eval import update_submission
from synorchestrator.eval import update_submission_run
from synorchestrator.eval import submission_queue

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def run_job(queue_id, wes_id, wf_jsonyaml, add_attachments=None):
    """
    Put a workflow in the queue and immmediately run it.
    """
    wf_config = queue_config()[queue_id]
    if wf_config['workflow_url'] is None:
        wf_config = fetch_queue_workflow(queue_id)
    wf_attachments = wf_config['workflow_attachments'] 
    if add_attachments is not None:
        wf_attachments += add_attachments
        wf_attachments = list(set(wf_attachments))

    wes_instance = WES(wes_id)
    request = {'workflow_url': wf_config['workflow_url'],
               'workflow_params': wf_jsonyaml,
               'attachment': wf_attachments}
    run_data = wes_instance.run_workflow(request)
    run_data['start_time'] = dt.datetime.now().ctime()
    run_status = wes_instance.get_run_status(run_data['run_id'])['state']
    run_data['status'] = run_status
    return run_data


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
    wf_jsonyaml = submission['data']
    logger.info(" Job parameters: '{}'".format(wf_jsonyaml))

    run_data = run_job(queue_id, wes_id, wf_jsonyaml)

    update_submission(queue_id, submission_id, 'run', run_data)
    update_submission(queue_id, submission_id, 'status', 'SUBMITTED')
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
        wes_instance = WES(sub_log['wes_id'])
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
