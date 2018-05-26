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
    # run_data = {'workflow_id': 'cebafa4f-53d8-41a3-9925-700cb2c407c5'}
    run_data = client.run_workflow(submission['data'])
    eval.update_submission_run(eval_id, submission_id, run_data)
    eval.update_submission_status(eval_id, submission_id, 'SUBMITTED')


def run_eval(eval_id, wes_id=None):
    """
    Run all submissions in a queue in a single environment.
    """
    for submission_id in eval.get_submissions(eval_id):
        run_submission(eval_id, submission_id, wes_id)


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
    # wes_request = util.build_wes_request(
    #     workflow_url=checker_descriptor['url'],
    #     workflow_params=checker_tests[0]['url'],
    #     workflow_type=checker_descriptor['type']
    # )
    wes_request = util.build_wes_request(
        workflow_descriptor=checker_descriptor['descriptor'],
        workflow_params=checker_tests[0]['url'],
        workflow_type=checker_descriptor['type']
    )
    eval.create_submission(eval_id, wes_request, wes_id)
    if not queue_only:
        run_eval(eval_id, wes_id)
    else:
        return 0


def monitor(eval_ids, submission_ids=None, start=None):
    """
    Monitor progress of workflow jobs.
    """
    if start is None:
        start = dt.datetime.now()

    eval_submission_runs = {}
    submission_type = 'checker'
    for eval_id in eval_ids:
        eval_name = os.path.basename(config.eval_config[eval_id]['workflow_id'])
        submission_ids = eval.get_submissions(eval_id, status='SUBMITTED')
        for submission_id in submission_ids:
            bundle = eval.get_submission_bundle(eval_id, submission_id)
            try:
                workflow_id = bundle['run']['workflow_id']
            except KeyError:
                workflow_id = 'pending'
            client = WESClient(**config.wes_config[bundle['wes_id']])
            run = client.get_workflow_run_status(workflow_id)
            eval_submission_runs.setdefault(eval_name, {})[submission_id] = {
                'job': submission_type,
                'wes': bundle['wes_id'],
                'run_id': run['workflow_id'],
                'run_status': run['state']
            }
    status_df = pd.DataFrame.from_dict(
        {(i, j): eval_submission_runs[i][j]
         for i in eval_submission_runs.keys()
         for j in eval_submission_runs[i].keys()},
        orient='index'
    )

    clear_output(wait=True)
    t = dt.datetime.now()
    print('Time elapsed: {}\n'.format(util.convert_timedelta(t - start)))
    display(status_df)
    sys.stdout.flush()
    if any(status_df['run_status'].isin(['QUEUED', 'INITIALIZING', 'RUNNING'])):
        time.sleep(1)
        monitor(eval_ids, start=start)
    else:
        return status_df


def run_all(eval_wes_map, checker=True, monitor_jobs=True):
    """
    Run all submissions for multiple queues in multiple environments
    (cross product of queues, workflow service endpoints).
    """
    for eval_id in eval_wes_map:
        [run_checker(eval_id, wes_id) for wes_id in eval_wes_map[eval_id]]
    t0 = dt.datetime.now()
    [run_eval(eval_id) for eval_id in eval_wes_map]
    if monitor_jobs:
        monitor(eval_wes_map.keys(), start=t0)
