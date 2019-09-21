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
import json
import datetime as dt

from IPython.display import display, clear_output

from ga4ghtest.core.config import queue_config, wes_config
from ga4ghtest.util import ctime2datetime, convert_timedelta
from ga4ghtest.services.wes import WESService
from ga4ghtest.converters.trs2wes import store_verification
from ga4ghtest.converters.trs2wes import build_wes_request
from ga4ghtest.converters.trs2wes import fetch_queue_workflow
from ga4ghtest.core.queue import get_submission_bundle
from ga4ghtest.core.queue import get_submissions
from ga4ghtest.core.queue import create_submission
from ga4ghtest.core.queue import update_submission

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def run_job(queue_id,
            wes_id,
            wf_jsonyaml,
            opts=None,
            add_attachments=None,
            submission=False):
    """
    Put a workflow in the queue and immmediately run it.

    :param str queue_id: String identifying the workflow queue.
    :param str wes_id:
    :param str wf_jsonyaml:
    :param dict opts:
    :param list add_attachments:
    :param bool submission:
    """
    wf_config = queue_config()[queue_id]
    if wf_config['workflow_url'] is None:
        wf_config = fetch_queue_workflow(queue_id)
    wf_attachments = wf_config['workflow_attachments']
    if add_attachments is not None:
        wf_attachments += add_attachments
        wf_attachments = list(set(wf_attachments))

    if not submission:
        submission_id = create_submission(queue_id=queue_id,
                                        submission_data=wf_jsonyaml,
                                        wes_id=wes_id)
    wes_instance = WESService(wes_id)
    service_config = wes_config()[wes_id]
    request = {'workflow_url': wf_config['workflow_url'],
            'workflow_params': wf_jsonyaml,
            'attachment': wf_attachments}

    parts = []
    if opts is not None:
        parts = build_wes_request(
            workflow_file=request['workflow_url'],
            jsonyaml=request['workflow_params'],
            attachments=request['attachment'],
            **opts
        )
    if 'workflow_engine_parameters' in service_config:
        parts.append(('workflow_engine_parameters',
                    json.dumps(service_config['workflow_engine_parameters'])))
    parts = parts if len(parts) else None

    run_log = wes_instance.run_workflow(request, parts=parts)
    if run_log['run_id'] == 'failed':
        logger.info("Job submission failed for WES '{}'"
                    .format(wes_id))
        run_status = 'FAILED'
        sub_status = 'FAILED'
    else:
        logger.info("Job received by WES '{}', run ID: {}"
                    .format(wes_id, run_log['run_id']))
        run_log['start_time'] = dt.datetime.now().ctime()
        time.sleep(10)
        run_status = wes_instance.get_run_status(run_log['run_id'])['state']
        sub_status = 'SUBMITTED'
    run_log['status'] = run_status

    if not submission:
        update_submission(queue_id, submission_id, 'run_log', run_log)
        update_submission(queue_id, submission_id, 'status', sub_status)
    return run_log


def run_submission(queue_id,
                   submission_id,
                   wes_id=None,
                   opts=None):
    """
    For a single submission to a single evaluation queue, run
    the workflow in a single environment.

    :param str queue_id: String identifying the workflow queue.
    :param str submission_id:
    :param str wes_id:
    :param dict opts:
    """
    submission = get_submission_bundle(queue_id, submission_id)
    if submission['wes_id'] is not None:
        wes_id = submission['wes_id']

    logger.info(" Submitting to WES endpoint '{}':"
                " \n - submission ID: {}"
                .format(wes_id, submission_id))
    wf_jsonyaml = submission['data']
    logger.info(" Job parameters: '{}'".format(wf_jsonyaml))

    run_log = run_job(queue_id=queue_id,
                      wes_id=wes_id,
                      wf_jsonyaml=wf_jsonyaml,
                      submission=True,
                       dopts=opts)

    update_submission(queue_id, submission_id, 'run_log', run_log)
    update_submission(queue_id, submission_id, 'status', 'SUBMITTED')
    return run_log


def run_queue(queue_id, wes_id=None, opts=None):
    """
    Run all submissions in a queue in a single environment.

    :param str queue_id: String identifying the workflow queue.
    :param str wes_id:
    :param dict opts:
    """
    queue_log = {}
    for submission_id in get_submissions(queue_id, status='RECEIVED'):
        submission = get_submission_bundle(queue_id, submission_id)
        if submission['wes_id'] is not None:
            wes_id = submission['wes_id']
        run_log = run_submission(queue_id=queue_id,
                                submission_id=submission_id,
                                wes_id=wes_id,
                                opts=opts)
        run_log['wes_id'] = wes_id
        queue_log[submission_id] = run_log

    return queue_log


def monitor_queue(queue_id):
    """
    Update the status of all submissions for a queue.

        queue_id (str): string identifying the workflow queue.
    """
    current = dt.datetime.now()
    queue_log = {}
    for sub_id in get_submissions(queue_id=queue_id):
        submission = get_submission_bundle(queue_id, sub_id)
        if submission['status'] == 'RECEIVED':
            queue_log[sub_id] = {'status': 'PENDING'}
            continue
        run_log = submission['run_log']
        if run_log['run_id'] == 'failed':
            queue_log[sub_id] = {'status': 'FAILED'}
            continue
        run_log['wes_id'] = submission['wes_id']
        if run_log['status'] in ['COMPLETE', 'CANCELED', 'EXECUTOR_ERROR']:
            queue_log[sub_id] = run_log
            continue
        wes_instance = WESService(submission['wes_id'])
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
            sub_status = run_log['status']
            if wf_config['target_queue']:
                # store_verification(wf_config['target_queue'],
                #                    submission['wes_id'])
                sub_status = 'VALIDATED'
            update_submission(queue_id, sub_id, 'status', sub_status)

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

            for queue_id in queue_config():
                queue_status = monitor_queue(queue_id)
                if len(queue_status):
                    statuses.append(queue_status)
                    print("\nWorkflow queue: {}".format(queue_id))
                    status_tracker = pd.DataFrame.from_dict(
                        queue_status,
                        orient='index')

                    display(status_tracker)

            terminal_statuses = ['FAILED',
                                'COMPLETE',
                                'CANCELED',
                                'EXECUTOR_ERROR']
            if all([sub['status'] in terminal_statuses
                    for queue in statuses
                    for sub in queue.values()]):
                print("\nNo jobs running...")
            print("\n(Press CTRL+C to quit)")
            time.sleep(2)
            os.system('clear')
            sys.stdout.flush()

    except KeyboardInterrupt:
        print("\nDone")
        return
