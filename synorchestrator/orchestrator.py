#!/usr/bin/env python
"""
Takes a given ID/URL for a workflow registered in a given TRS
implementation; prepare the workflow run request, including
retrieval and formatting of parameters, if not provided; post
the workflow run request to a given WES implementation;
monitor and report results of the workflow run.
"""
import logging
import os
import sys
import yaml
import time
import pandas as pd
import datetime as dt
from IPython.display import display, clear_output

from synorchestrator import config
from synorchestrator import util
from synorchestrator import eval
from synorchestrator.trs.client import TRSClient
from synorchestrator.wes.client import WESClient

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
pd.set_option('display.width', 100)

def run_submission(eval_id, submission_id, wes_id='local'):
    """
    For a single submission to a single evaluation queue, run
    the workflow in a single environment.
    """
    submission = eval.get_submission_bundle(eval_id, submission_id)
    if submission['wes_id'] is not None:
        wes_id = submission['wes_id']
    logger.info("Submitting job '{}' for eval '{}' to WES endpoint '{}'"
                .format(submission_id, eval_id, wes_id))
    client = WESClient(**config.wes_config[wes_id])
    run_data = client.run_workflow(submission['data'])
    run_data['start_time'] = dt.datetime.now().ctime()
    eval.update_submission_run(eval_id, submission_id, run_data)
    eval.update_submission_status(eval_id, submission_id, 'SUBMITTED')
    return eval.get_submission_bundle(eval_id, submission_id)


def run_eval(eval_id, wes_id=None):
    """
    Run all submissions in a queue in a single environment.
    """
    eval_name = os.path.basename(config.eval_config[eval_id]['workflow_id'])
    submission_dict = {}
    for submission_id in eval.get_submissions(eval_id):
        bundle = run_submission(eval_id, submission_id, wes_id)
        submission_dict.setdefault(eval_name, {})[submission_id] = {
            'queue_id': eval_id,
            'job': bundle['type'],
            'submission_status': bundle['status'],
            'wes_id': bundle['wes_id'],
            'run_id': bundle['run']['workflow_id'],
            'run_status': 'SUBMITTED',
            'start_time': bundle['run']['start_time']
        }
    return submission_dict


def run_checker(eval_id, wes_id, queue_only=True):
    """
    Run checker workfllow for an evaluation workflow in a single
    environment.
    """
    workflow_config = config.eval_config[eval_id]
    workflow_config['id'] = workflow_config['workflow_id']
    logger.info("Preparing checker workflow run request for '{}' from  '{}''"
                .format(workflow_config['id'], workflow_config['trs_id']))
    client = TRSClient(**config.trs_config[workflow_config['trs_id']])
    checker_workflow = client.get_workflow_checker(workflow_config['id'])
    checker_descriptor = client.get_workflow_descriptor(
        id=checker_workflow['id'],
        version_id=workflow_config['version_id'],
        type=workflow_config['workflow_type']
    )
    checker_tests = client.get_workflow_tests(
        id=checker_workflow['id'],
        version_id=workflow_config['version_id'],
        type=workflow_config['workflow_type']
    )
    wes_request = util.build_wes_request(
        workflow_descriptor=checker_descriptor['descriptor'],
    #     workflow_url=checker_descriptor['url'],
        workflow_params=checker_tests[0]['url'],
        workflow_type=checker_descriptor['type']
    )
    submission_id = eval.create_submission(
        eval_id, wes_request, wes_id, type='checker'
    )
    if not queue_only:
        return run_eval(eval_id, wes_id)
    else:
        return submission_id


def monitor(submissions, eval_ids=None, submission_ids=None):
    """
    Monitor progress of workflow jobs.
    """
    current = dt.datetime.now()

    status_dict = {}
    for submission_dict in submissions:
        for eval_id in submission_dict:
            for submission_id, bundle in submission_dict[eval_id].items():
                client = WESClient(**config.wes_config[bundle['wes_id']])
                run = client.get_workflow_run_status(bundle['run_id'])
                status_dict.setdefault(eval_id, {})[submission_id] = {
                    'queue_id': eval_id,
                    'job': bundle['job'],
                    'submission_status': bundle['submission_status'],
                    'wes_id': bundle['wes_id'],
                    'run_id': run['workflow_id'],
                    'run_status': run['state'],
                    'start_time': bundle['start_time'],
                    'elapsed_time': util.convert_timedelta(
                        current - util.ctime2datetime(bundle['start_time'])
                    )
                }

    status_df = pd.DataFrame.from_dict(
        {(i, j): status_dict[i][j]
         for i in status_dict.keys()
         for j in status_dict[i].keys()},
        orient='index'
    )

    clear_output(wait=True)
    display(status_df)
    sys.stdout.flush()
    if any(status_df['run_status'].isin(['QUEUED', 'INITIALIZING', 'RUNNING'])):
        time.sleep(1)
        monitor(status_dict)
    else:
        print("Done")


def run_all(eval_wes_map, checker=True, monitor_jobs=False):
    """
    Run all submissions for multiple queues in multiple environments
    (cross product of queues, workflow service endpoints).
    """
    for eval_id in eval_wes_map:
        submission_ids = [run_checker(eval_id, wes_id)
                          for wes_id in eval_wes_map[eval_id]]
    t0 = dt.datetime.now()
    submissions = [run_eval(eval_id) for eval_id in eval_wes_map]
    if monitor_jobs:
        submissions = monitor(eval_wes_map.keys())
    return submissions
