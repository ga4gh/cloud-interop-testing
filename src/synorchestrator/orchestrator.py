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

from synorchestrator.config import wes_config, wf_config
from synorchestrator.util import ctime2datetime, convert_timedelta
from synorchestrator.wes.client import WESClient
from synorchestrator.util import get_json, save_json

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def queue_path():
    queue_loc = os.path.join(os.path.expanduser('~'), 'submission_queue.json')
    # if the file does not exist, create a blank template
    if not os.path.exists(queue_loc):
        with open(queue_loc, 'w') as f:
            f.write('{}\n')
    return queue_loc


def create_submission(wes_id, submission_data, wf_type, wf_name, sample):
    submissions = get_json(queue_path())
    submission_id = dt.datetime.now().strftime('%d%m%d%H%M%S%f')

    submissions.setdefault(wes_id, {})[submission_id] = {'status': 'RECEIVED',
                                                         'data': submission_data,
                                                         'wf_id': wf_name,
                                                         'type': wf_type,
                                                         'sample': sample}
    save_json(queue_path(), submissions)
    logger.info(" Queueing Job for '{}' endpoint:"
                "\n - submission ID: {}".format(wes_id, submission_id))
    return submission_id


def get_submissions(wes_id, status='RECEIVED'):
    """Return all ids with the requested status."""
    submissions = get_json(queue_path())
    if wes_id not in submissions:
        return []
    return [id for id, bundle in submissions[wes_id].items() if bundle['status'] == status]


def get_submission_bundle(wes_id, submission_id):
    """Return the submission's info."""
    return get_json(queue_path())[wes_id][submission_id]


def update_submission(wes_id, submission_id, param, status):
    """Update the status of a submission."""
    submissions = get_json(queue_path())
    submissions[wes_id][submission_id][param] = status
    save_json(queue_path(), submissions)


def update_submission_run(wes_id, submission_id, param, status):
    """Update the status of a submission."""
    submissions = get_json(queue_path())
    submissions[wes_id][submission_id]['run'][param] = status
    save_json(queue_path(), submissions)


def set_queue_from_user_json(filepath):
    """
    Intended to take a user json-config file and submit the contents as queued workflows.

    Example:

   {"local":
       {"NWD119836":
          {"wf_name": "wdl_UoM_align",
           "jsonyaml": "file:///home/quokka/git/current_demo/orchestrator/tests/data/NWD119836.json"},
        "NWD136397":
          {"wf_name": "wdl_UoM_align",
           "jsonyaml": "file:///home/quokka/git/current_demo/orchestrator/tests/data/NWD136397.json"}
   },
    "aws-toil-server":
       {"NWD119836":
          {"wf_name": "wdl_UoM_align",
           "jsonyaml": "file:///home/quokka/git/current_demo/orchestrator/tests/data/NWD119836.json"},
        "NWD136397":
          {"wf_name": "wdl_UoM_align",
           "jsonyaml": "file:///home/quokka/git/current_demo/orchestrator/tests/data/NWD136397.json"}}}

    This config would submit two samples each (named NWD119836 & NWD136397) to the workflow services:
    local and aws-toil-server respectively, retrieving configuration details that had been set for those
    services in stored_templates.json.
    """
    # TODO verify terms match between configs
    sdict = get_json(filepath)
    for wf_service in sdict:
        for sample in sdict[wf_service]:
            wf_name = sdict[wf_service][sample]['wf_name']
            wf_jsonyaml = sdict[wf_service][sample]['jsonyaml']
            print('Queueing "{}" on "{}" with data: {}'.format(wf_name, wf_service, sample))
            queue(wf_service, wf_name, wf_jsonyaml, sample)


def queue(service, wf_name, wf_jsonyaml, sample='NA', attach=None):
    """
    Put a workflow in the queue.

    :param service:
    :param wf_name:
    :param wf_jsonyaml:
    :param sample:
    :param attach:
    :return:
    """
    # fetch workflow params from config file
    # synorchestrator.config.add_workflow() can be used to add a workflow to this file
    if wf_name not in wf_config():
        raise ValueError(wf_name + ' not found in configuration file.  '
                         'To add ' + wf_name + ' to the configuration file, '
                         'use: synorchestrator.config.add_workflow().')
    wf = wf_config()[wf_name]

    if not attach and wf['workflow_attachments']:
        attach = wf['workflow_attachments']
    else:
        attach = []

    submission_id = create_submission(wes_id=service,
                                      submission_data={'wf': wf['workflow_url'],
                                                       'jsonyaml': wf_jsonyaml,
                                                       'attachments': attach},
                                      wf_name=wf_name,
                                      wf_type=wf['workflow_type'],
                                      sample=sample)
    return submission_id


def no_queue_run(service, wf_name, wf_jsonyaml, sample='NA', attach=None):
    """
    Put a workflow in the queue and immmediately run it.

    :param service:
    :param wf_name:
    :param wf_jsonyaml:
    :param sample:
    :param attach:
    :return:
    """
    submission_id = queue(service, wf_name, wf_jsonyaml, sample=sample, attach=attach)
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
    run_data = client.run(submission['data']['wf'],
                          submission['data']['jsonyaml'],
                          submission['data']['attachments'])
    run_data['start_time'] = dt.datetime.now().ctime()
    update_submission(wes_id, submission_id, 'run', run_data)
    update_submission(wes_id, submission_id, 'status', 'SUBMITTED')
    return run_data


def services_w_wfs_left2run():
    services = []
    for wf_service in wes_config():
        received_submissions = get_submissions(wf_service, status='RECEIVED')
        if received_submissions:
            services.append(wf_service)
    return services


def service_ready(service):
    if get_submissions(service, status='SUBMITTED'):
        return False
    return True


def run_all():
    """
    Run all jobs with the status: RECEIVED in the submission queue.

    Check the status of each job per workflow service for status: COMPLETE
    before running the next queued job.
    """
    services = services_w_wfs_left2run()
    while services:
        try:
            for service in services:
                if service_ready(service):
                    received_submissions = sorted(get_submissions(service, status='RECEIVED'))
                    try:
                        run_submission(service, received_submissions[0])
                    except ConnectionError:
                        pass
            services = services_w_wfs_left2run()
        except ValueError:
            pass
        time.sleep(8)


def monitor_service(wf_service):
    """
    Returns a dictionary of all of the jobs under a single wes service appropriate
    for displaying as a pandas dataframe.

    :param wf_service:
    :return:
    """
    status_dict = {}
    submissions = get_json(queue_path())
    for run_id in submissions[wf_service]:
        sample_name = submissions[wf_service][run_id]['sample']
        if 'run' not in submissions[wf_service][run_id]:
            status_dict.setdefault(wf_service, {})[run_id] = {
                'wf_id': submissions[wf_service][run_id]['wf_id'],
                'run_id': '-',
                'sample_name': sample_name,
                'run_status': 'QUEUED',
                'start_time': '-',
                'elapsed_time': '-'}
        else:
            if submissions[wf_service][run_id]['status'] in ['COMPLETE', 'SYSTEM_ERROR', 'EXECUTOR_ERROR']:
                run = submissions[wf_service][run_id]['run']
                try:
                    wf_id = run['workflow_id']
                except KeyError:
                    wf_id = run['run_id']
                status_dict.setdefault(wf_service, {})[run_id] = {
                    'wf_id': submissions[wf_service][run_id]['wf_id'],
                    'run_id': wf_id,
                    'sample_name': sample_name,
                    'run_status': submissions[wf_service][run_id]['status'],
                    'start_time': run['start_time'],
                    'elapsed_time': run['elapsed_time']}
            else:
                try:
                    run = submissions[wf_service][run_id]['run']
                    if 'run_id' not in run and 'workflow_id' not in run:
                        status_dict.setdefault(wf_service, {})[run_id] = {
                            'wf_id': submissions[wf_service][run_id]['wf_id'],
                            'run_id': '-',
                            'sample_name': sample_name,
                            'run_status': 'INITIALIZING',
                            'start_time': '-',
                            'elapsed_time': '-'}
                    else:
                        client = WESClient(wes_config()[wf_service])
                        try:
                            wf_id = run['workflow_id']
                        except KeyError:
                            wf_id = run['run_id']
                        if 'state' not in run:
                            run['state'] = client.get_run_status(wf_id)['state'].upper()
                        elif run['state'].upper() not in ['COMPLETED', 'OK', 'EXECUTOR_ERROR', 'SYSTEM_ERROR']:
                            run['state'] = client.get_run_status(wf_id)['state'].upper()

                        if run['state'] in ['QUEUED', 'INITIALIZING', 'RUNNING']:
                            etime = convert_timedelta(dt.datetime.now() - ctime2datetime(run['start_time']))
                        elif 'elapsed_time' not in run:
                            etime = '0h:0m:0s'
                        else:
                            update_submission(wf_service, run_id, 'status', run['state'])
                            etime = run['elapsed_time']
                        update_submission_run(wf_service, run_id, 'elapsed_time', etime)
                        status_dict.setdefault(wf_service, {})[run_id] = {
                            'wf_id': submissions[wf_service][run_id]['wf_id'],
                            'run_id': wf_id,
                            'sample_name': sample_name,
                            'run_status': run['state'],
                            'start_time': run['start_time'],
                            'elapsed_time': etime}
                except ConnectionError:
                    status_dict.setdefault(wf_service, {})[run_id] = {
                        'wf_id': 'ConnectionError',
                        'run_id': '-',
                        'sample_name': sample_name,
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
        submissions = get_json(queue_path())

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
        time.sleep(2)
