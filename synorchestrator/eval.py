import logging
import os
import datetime as dt

from synorchestrator.util import get_json, save_json

logger = logging.getLogger(__name__)

submission_queue = os.path.join(os.path.dirname(__file__), 'submission_queue.json')


def create_submission(wes_id, submission_data, wf_type='cwl', wf_name='wflow0'):
    """
    Submit a new job request to an evaluation queue.

    Both type and wf_name are optional but could be used with TRS.
    """
    submissions = get_json(submission_queue)
    submission_id = dt.datetime.now().strftime('%d%m%d%H%M%S%f')

    submissions.setdefault(wes_id, {})[submission_id] = {'status': 'RECEIVED',
                                                         'data': submission_data,
                                                         'wf_id': wf_name,
                                                         'type': wf_type}
    save_json(submission_queue, submissions)
    logger.info(" Queueing Job for '{}' endpoint:"
                "\n - submission ID: {}".format(wes_id, submission_id))
    return submission_id


def get_submissions(wes_id, status='RECEIVED'):
    """Return all ids with the requested status."""
    submissions = get_json(submission_queue)
    return [id for id, bundle in submissions[wes_id].items() if bundle['status'] == status]


def get_submission_bundle(wes_id, submission_id):
    """Return the submission's info."""
    return get_json(submission_queue)[wes_id][submission_id]


def update_submission(wes_id, submission_id, param, status):
    """Update the status of a submission."""
    submissions = get_json(submission_queue)
    submissions[wes_id][submission_id][param] = status
    save_json(submission_queue, submissions)


def update_submission_run(wes_id, submission_id, param, status):
    """Update the status of a submission."""
    submissions = get_json(submission_queue)
    submissions[wes_id][submission_id]['run'][param] = status
    save_json(submission_queue, submissions)
