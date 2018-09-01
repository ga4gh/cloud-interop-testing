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

from synorchestrator.config import queue_config
from synorchestrator.util import get_json, ctime2datetime, convert_timedelta
from synorchestrator.wes.wrapper import WES
from synorchestrator.trs2wes import fetch_queue_workflow
from synorchestrator.trs2wes import store_verification
from synorchestrator.queue import get_submission_bundle
from synorchestrator.queue import get_submissions
from synorchestrator.queue import update_submission
from synorchestrator.queue import submission_queue

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
    run_log = wes_instance.run_workflow(request)
    run_log['start_time'] = dt.datetime.now().ctime()
    run_status = wes_instance.get_run_status(run_log['run_id'])['state']
    run_log['status'] = run_status
    return run_log


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

    run_log = run_job(queue_id, wes_id, wf_jsonyaml)

    update_submission(queue_id, submission_id, 'run_log', run_log)
    update_submission(queue_id, submission_id, 'status', 'SUBMITTED')
    return run_log


def run_queue(queue_id, wes_id=None):
    """
    Run all submissions in a queue in a single environment.
    """
    queue_log = {}
    for submission_id in get_submissions(queue_id, status='RECEIVED'):
        submission = get_submission_bundle(queue_id, submission_id)
        if submission['wes_id'] is not None:
            wes_id = submission['wes_id']
        run_log = run_submission(queue_id, submission_id, wes_id)
        run_log['wes_id'] = wes_id
        queue_log[submission_id] = run_log

    return queue_log


def run_all():
    """
    Run all jobs with the status: RECEIVED across all evaluation queues.
    Check the status of each submission per queue for status: COMPLETE
    before running the next queued submission.
    """
    orchestrator_log = {}
    for queue_id in queue_config():
        orchestrator_log[queue_id] = run_queue(queue_id)
    return orchestrator_log


def monitor_queue(queue_id):
    """
    Update the status of all submissions for a queue.
    """
    current = dt.datetime.now()
    queue_log = {}
    for sub_id in get_submissions(queue_id, status='SUBMITTED'):
        submission = get_submission_bundle(queue_id, sub_id)
        run_log = submission['run_log']
        wes_instance = WES(submission['wes_id'])
        run_status = wes_instance.get_run_status(run_log['run_id'])
        
        if run_status['state'] in ['QUEUED', 'INITIALIZING', 'RUNNING']:
            etime = convert_timedelta(
                current - ctime2datetime(run_log['start_time'])
            )
        elif 'elapsed_time' not in run_log:
            etime = 0
        else:
            etime = run_log['elapsed_time']

        run_log['status'] = run_status['state']
        run_log['elapsed_time'] = etime

        update_submission(queue_id, sub_id, 'run_log', run_log)
        
        if run_log['status'] == 'COMPLETE':
            wf_config = queue_config()[queue_id]
            store_verification(wf_config['target_queue'], submission['wes_id'])
            update_submission(queue_id, sub_id, 'status', 'VALIDATED')

        run_log['wes_id'] = submission['wes_id']
        queue_log[sub_id] = run_log

    return queue_log


def monitor():
    """
    Monitor progress of workflow jobs.
    """
    import pandas as pd
    pd.set_option('display.width', 1000)
    pd.set_option('display.max_columns', 10)
    pd.set_option('display.expand_frame_repr', False)

    try:
        while True:
            statuses = []
            
            clear_output(wait=True)
            os.system('clear')

            for queue_id in queue_config():
                statuses.append(monitor_queue(queue_id))
            if all([status == {} for status in statuses]):
                print("No jobs running...")
            else:
                status_tracker = pd.DataFrame.from_dict(
                    {i: status[i]
                    for status in statuses
                    for i in status},
                    orient='index')

                display(status_tracker)
                sys.stdout.flush()

            time.sleep(1)
    except KeyboardInterrupt:
        print("\nDone")
        return

