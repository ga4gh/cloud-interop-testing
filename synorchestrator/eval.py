import logging
import os
import json
import datetime as dt

from synorchestrator import config
from synorchestrator.util import get_json, save_json

logger = logging.getLogger(__name__)

EVALS_PATH = os.path.join(os.path.dirname(__file__), '.evals')


def create_submission(eval_id, submission_data, wes_id, type=None):
    """
    Submit a new job request to an evaluation queue.
    """
    evals = get_json(EVALS_PATH)
    submission_id = dt.datetime.now().strftime('%d%m%d%H%M%S%f')

    evals.setdefault(eval_id, {})[submission_id] = {'status': 'RECEIVED',
                                                    'data': submission_data,
                                                    'wes_id': wes_id,
                                                    'type': type}
    save_json(EVALS_PATH, evals)
    logger.info("Created new job submission:\n - submission ID: {}".format(submission_id))
    logger.debug("\n - evaluation queue: {} ({})"
                 "\n - data:\n{}".format(eval_id,
                                         config.eval_config[eval_id]['workflow_id'],
                                         json.dumps(submission_data, indent=2)))
    return submission_id


def get_submissions(eval_id, status='RECEIVED'):
    """
    Return all submissions to a queue matching the specified status.

    RECEIVED is hard-coded on all job creations atm.
    """
    evals = get_json(EVALS_PATH)
    return [id for id, bundle in evals[eval_id].items() if bundle['status'] in status]


def get_submission_bundle(eval_id, submission_id):
    """
    Submit a new job request to an evaluation queue.
    """
    return get_json(EVALS_PATH)[eval_id][submission_id]


def update_submission_status(eval_id, submission_id, status):
    """
    Update the status of a submission.
    """
    evals = get_json(EVALS_PATH)
    evals[eval_id][submission_id]['status'] = status
    save_json(EVALS_PATH, evals)


def update_submission_run(eval_id, submission_id, run_data):
    """
    Update information for a workflow run.
    """
    evals = get_json(EVALS_PATH)
    evals[eval_id][submission_id]['run'] = run_data
    save_json(EVALS_PATH, evals)
