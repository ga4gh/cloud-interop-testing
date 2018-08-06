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
from requests.exceptions import ConnectionError
from IPython.display import display, clear_output
from synorchestrator.config import wes_config, eval_config, trs_config
from synorchestrator.util import get_json, ctime2datetime, convert_timedelta
from synorchestrator.wes.client import WESClient
from wes_client.util import get_status
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
    # synorchestrator.config.add_eval() can be used to add a workflow to this file
    wf = eval_config()[wf_name]

    submission_id = create_submission(wes_id=service,
                                      submission_data={'wf': wf['workflow_url'],
                                                       'jsonyaml': wf['workflow_jsonyaml'],
                                                       'attachments': wf['workflow_attachments']},
                                      wf_name=wf_name,
                                      wf_type=wf['workflow_type'])
    run_submission(service, submission_id)


def run_submission(wes_id, submission_id):
    """
    For a single submission to a single evaluation queue, run
    the workflow in a single environment.
    """
    submission = get_submission_bundle(wes_id, submission_id)

    logger.info(" Submitting to WES endpoint '{}':"
                " \n - submission ID: {}"
                .format(wes_id, submission_id))

    client = WESClient(wes_config()[wes_id])
    run_data = client.run_workflow(submission['data']['wf'],
                                   submission['data']['jsonyaml'],
                                   submission['data']['attachments'])
    run_data['start_time'] = dt.datetime.now().ctime()
    update_submission(wes_id, submission_id, 'run', run_data)
    update_submission(wes_id, submission_id, 'status', 'SUBMITTED')
    return run_data


def run_next_queued(wf_service):
    """
    Run the next submission slated for a single WES endpoint.

    Return None if no submissions are queued.
    """
    queued_submissions = get_submissions(wf_service, status='RECEIVED')
    if not queued_submissions:
        return False
    for submssn_id in sorted(queued_submissions):
        return run_submission(wf_service, submssn_id)


def run_all():
    """
    Run all jobs with the status: RECEIVED in the submission queue.

    Check the status of each job per workflow service for status: COMPLETE
    before running the next queued job.
    """
    current_job_state = {}
    for wf_service in wes_config():
        current_job_state[wf_service] = ''
    for wf_service in wes_config():
        submissions_left = True
        while submissions_left:
            submissions_left = run_next_queued(wf_service)
            if not submissions_left:
                break
            status = get_status(submissions_left['run_id'])
            while status != 'COMPLETE':
                time.sleep(4)


# def run_checker(eval_id, wes_id, queue_only=True):
#     """
#     Run checker workflow for an evaluation workflow in a single
#     environment.
#     """
#     import re
#     from synorchestrator.trs.client import TRSClient
#
#     workflow_config = eval_config[eval_id]
#     workflow_config['id'] = workflow_config['workflow_id']
#     logger.info("Preparing checker workflow run request for '{}' from  '{}''"
#                 .format(workflow_config['id'], workflow_config['trs_id']))
#     client = TRSClient(**trs_config[workflow_config['trs_id']])
#     checker_workflow = client.get_workflow_checker(workflow_config['id'])
#     checker_descriptor = client.get_workflow_descriptor(
#         id=checker_workflow['id'],
#         version_id=workflow_config['version_id'],
#         type=workflow_config['workflow_type']
#     )
#     if (checker_descriptor['type'] == 'CWL' and
#         re.search('run:', checker_descriptor['descriptor'])):
#         checker_descriptor['descriptor'] = get_packed_cwl(checker_descriptor['url'])
#     checker_tests = client.get_workflow_tests(
#         id=checker_workflow['id'],
#         version_id=workflow_config['version_id'],
#         type=workflow_config['workflow_type']
#     )
#     wes_request = build_wes_request(
#         workflow_descriptor=checker_descriptor['descriptor'],
#         workflow_params=checker_tests[0]['url'],
#         workflow_type=checker_descriptor['type']
#     )
#     submission_id = eval.create_submission(
#         eval_id, wes_request, wes_id, type='checker'
#     )
#     if not queue_only:
#         return run_eval(eval_id, wes_id)
#     else:
#         return submission_id


def monitor_service(wf_service):
    """
    Returns a dictionary of all of the jobs under a single wes service appropriate
    for displaying as a pandas dataframe.

    :param wf_service:
    :return:
    """
    status_dict = {}
    submissions = get_json(submission_queue)
    for run_id in submissions[wf_service]:
        if 'run' not in submissions[wf_service][run_id]:
            status_dict.setdefault(wf_service, {})[run_id] = {
                'wf_id': submissions[wf_service][run_id]['wf_id'],
                'run_id': '-',
                'run_status': 'QUEUED',
                'start_time': '-',
                'elapsed_time': '-'}
        else:
            try:
                run = submissions[wf_service][run_id]['run']
                client = WESClient(wes_config()[wf_service])
                run['state'] = client.get_workflow_run_status(run['run_id'])['state']
                if run['state'] in ['QUEUED', 'INITIALIZING', 'RUNNING']:
                    etime = convert_timedelta(dt.datetime.now() - ctime2datetime(run['start_time']))
                elif 'elapsed_time' not in run:
                    etime = '0h:0m:0s'
                else:
                    etime = run['elapsed_time']
                update_submission_run(wf_service, run_id, 'elapsed_time', etime)
                status_dict.setdefault(wf_service, {})[run_id] = {
                    'wf_id': submissions[wf_service][run_id]['wf_id'],
                    'run_id': run['run_id'],
                    'run_status': run['state'],
                    'start_time': run['start_time'],
                    'elapsed_time': etime}
            except ConnectionError:
                status_dict.setdefault(wf_service, {})[run_id] = {
                    'wf_id': 'ConnectionError',
                    'run_id': '-',
                    'run_status': '-',
                    'start_time': '-',
                    'elapsed_time': '-'}

    return status_dict


def monitor():
    """Monitor progress of workflow jobs."""
    import pandas as pd
    pd.set_option('display.width', 100)

    while True:
        statuses = []
        submissions = get_json(submission_queue)

        for wf_service in submissions:
            statuses.append(monitor_service(wf_service))

        status_df = pd.DataFrame.from_dict(
            {(i, j): status[i][j]
             for status in statuses
             for i in status.keys()
             for j in status[i].keys()},
            orient='index')

        clear_output(wait=True)
        os.system('clear')
        display(status_df)
        sys.stdout.flush()
        time.sleep(1)
