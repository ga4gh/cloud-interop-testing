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

from synorchestrator.config import Config
from synorchestrator.util import ctime2datetime, convert_timedelta
from synorchestrator.wes.client import WESClient
from synorchestrator.util import get_json, save_json

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class Orchestrator():

    def __init__(self, queue_path=None, config_path=None, args=None):
        self.config = Config(config_path) # Should be first. Many methods rely on config.
        self.queue_loc = self.create_queue_json(queue_path)

    def create_queue_json(self, given=None):
        """
        Create a submission queue file if one does not exist.

        This method's name is somewhat of a misnomer. This method abstracts the checking for the file away from the init.
        It will only create the submission queue file if it does not already exist. This allows the user the specify a
        location in the init which could point to an existing file or the location where they want a new one to be created.
        """
        queue_loc = given or os.path.join(os.path.expanduser('~'), 'submission_queue.json')
        if not os.path.exists(queue_loc):
            with open(queue_loc, 'w') as f:
                f.write('{}\n')
        return queue_loc

    @property
    def queue_path(self):
        return self.queue_loc

    def create_submission(self, wes_id, submission_data, wf_type, wf_name, sample):
        submissions = get_json(self.queue_path)
        submission_id = dt.datetime.now().strftime('%d%m%d%H%M%S%f')

        submissions.setdefault(wes_id, {})[submission_id] = {'status': 'RECEIVED',
                                                             'data': submission_data,
                                                             'wf_id': wf_name,
                                                             'type': wf_type,
                                                             'sample': sample}
        save_json(self.queue_path, submissions)
        logger.info(" Queueing Job for '{}' endpoint:"
                    "\n - submission ID: {}".format(wes_id, submission_id))
        return submission_id

    def get_submissions(self, wes_id, status='RECEIVED'):
        """Return all ids with the requested status."""
        submissions = get_json(self.queue_path)
        if wes_id not in submissions:
            return []
        return [id for id, bundle in submissions[wes_id].items() if bundle['status'] == status]

    def get_submission_bundle(self, wes_id, submission_id):
        """Return the submission's info."""
        return get_json(self.queue_path)[wes_id][submission_id]

    def update_submission(self, wes_id, submission_id, param, status):
        """Update the status of a submission."""
        submissions = get_json(self.queue_path)
        submissions[wes_id][submission_id][param] = status
        save_json(self.queue_path, submissions)

    def update_submission_run(self, wes_id, submission_id, param, status):
        """Update the status of a submission."""
        submissions = get_json(self.queue_path)
        submissions[wes_id][submission_id]['run'][param] = status
        save_json(self.queue_path, submissions)

    def set_queue_from_user_json(self, filepath):
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
                self.queue(wf_service, wf_name, wf_jsonyaml, sample)

    def queue(self, service, wf_name, wf_jsonyaml, sample='NA', attach=None):
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
        # synorchestrator.config.Config.add_workflow() can be used to add a workflow to this file
        if wf_name not in self.config.wf_config():
            raise ValueError(wf_name + ' not found in configuration file.  '
                             'To add ' + wf_name + ' to the configuration file, '
                             'use: synorchestrator.config.add_workflow().')
        wf = self.config.wf_config()[wf_name]

        if not attach and wf['workflow_attachments']:
            attach = wf['workflow_attachments']
        else:
            attach = []

        submission_id = self.create_submission(wes_id=service,
                                          submission_data={'wf': wf['workflow_url'],
                                                           'jsonyaml': wf_jsonyaml,
                                                           'attachments': attach},
                                          wf_name=wf_name,
                                          wf_type=wf['workflow_type'],
                                          sample=sample)
        return submission_id

    def no_queue_run(self, service, wf_name, wf_jsonyaml, sample='NA', attach=None):
        """
        Put a workflow in the queue and immmediately run it.

        :param service:
        :param wf_name:
        :param wf_jsonyaml:
        :param sample:
        :param attach:
        :return:
        """
        submission_id = self.queue(service, wf_name, wf_jsonyaml, sample=sample, attach=attach)
        self.run_submission(service, submission_id)

    def run_submission(self, wes_id, submission_id):
        """
        For a single submission to a single evaluation queue, run
        the workflow in a single environment.
        """
        submission = self.get_submission_bundle(wes_id, submission_id)

        logger.info(" Submitting to WES endpoint '{}':"
                    " \n - submission ID: {}"
                    .format(wes_id, submission_id))

        client = WESClient(self.config.wes_config()[wes_id])
        run_data = client.run(submission['data']['wf'],
                              submission['data']['jsonyaml'],
                              submission['data']['attachments'])
        run_data['start_time'] = dt.datetime.now().ctime()
        self.update_submission(wes_id, submission_id, 'run', run_data)
        self.update_submission(wes_id, submission_id, 'status', 'SUBMITTED')
        return run_data

    def services_w_wfs_left2run(self):
        services = []
        for wf_service in self.config.wes_config():
            received_submissions = self.get_submissions(wf_service, status='RECEIVED')
            if received_submissions:
                services.append(wf_service)
        return services

    def service_ready(self, service):
        if self.get_submissions(service, status='SUBMITTED'):
            return False
        return True

    def run_all(self):
        """
        Run all jobs with the status: RECEIVED in the submission queue.

        Check the status of each job per workflow service for status: COMPLETE
        before running the next queued job.
        """
        services = self.services_w_wfs_left2run()
        while services:
            try:
                for service in services:
                    if self.service_ready(service):
                        received_submissions = self.get_submissions(service, status='RECEIVED')
                        try:
                            self.run_submission(service, received_submissions[0])
                        except ConnectionError:
                            pass
                services = self.services_w_wfs_left2run()
            except ValueError:
                pass
            time.sleep(8)

    def monitor_service(self, wf_service):
        """
        Returns a dictionary of all of the jobs under a single wes service appropriate
        for displaying as a pandas dataframe.

        :param wf_service:
        :return:
        """
        status_dict = {}
        submissions = get_json(self.queue_path)
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
                try:
                    run = submissions[wf_service][run_id]['run']

                    client = WESClient(self.config.wes_config()[wf_service])
                    try:
                        wf_id = run['workflow_id']
                    except KeyError:
                        wf_id = run['run_id']
                    run['state'] = client.get_run_status(wf_id)['state'].upper()
                    if run['state'] in ['QUEUED', 'INITIALIZING', 'RUNNING']:
                        etime = convert_timedelta(dt.datetime.now() - ctime2datetime(run['start_time']))
                    elif 'elapsed_time' not in run:
                        etime = '0h:0m:0s'
                    else:
                        self.update_submission(wf_service, run_id, 'status', run['state'])
                        etime = run['elapsed_time']
                    self.update_submission_run(wf_service, run_id, 'elapsed_time', etime)
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

    def monitor(self):
        """Monitor progress of workflow jobs."""
        import pandas as pd
        pd.set_option('display.width', 100)

        while True:
            statuses = []
            submissions = get_json(self.queue_path)

            for wf_service in submissions:
                statuses.append(self.monitor_service(wf_service))

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
