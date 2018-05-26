import logging
import os
import ruamel.yaml as yaml
import json
import datetime as dt

from synorchestrator import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

EVALS_PATH = os.path.join(os.path.dirname(__file__), '.evals')


def _get_evals():
    """
    Get status of evaluation queues.
    """
    try:
        with open(EVALS_PATH, 'r') as f:
            return json.load(f)
    except IOError as e:
        return {}


def _save_evals(evals):
    """
    Update orchestrator config file.
    """
    with open(EVALS_PATH, 'w') as f:
        json.dump(evals, f)


def create_submission(eval_id, submission_data, wes_id):
    """
    Submit a new job request to an evaluation queue.
    """
    evals = _get_evals()
    submission_id = dt.datetime.now().strftime('%d%m%d%H%M%S%f')

    evals.setdefault(eval_id, {})[submission_id] = {
        'status': 'RECEIVED',
        'data': submission_data,
        'wes_id': wes_id
    }
    _save_evals(evals)
    logger.info("Created new job submission:\n - evaluation queue: {} ({})\n"
                " - submission ID: '{}'\n - data:\n{}"
                .format(eval_id, config.eval_config[eval_id]['workflow_id'],
                        submission_id, json.dumps(submission_data, indent=2)))
    return submission_id


def get_submissions(eval_id, status='RECEIVED'):
    """
    Return all submissions to a queue matching the specified status.
    """
    evals = _get_evals()
    return [id for id, bundle in evals[eval_id].items()
            if bundle['status'] in status]


def get_submission_bundle(eval_id, submission_id):
    """
    Submit a new job request to an evaluation queue.
    """
    evals = _get_evals()
    return evals[eval_id][submission_id]


def update_submission_status(eval_id, submission_id, status):
    """
    Update the status of a submission.
    """
    evals = _get_evals()
    evals[eval_id][submission_id]['status'] = status
    _save_evals(evals)


def update_submission_run(eval_id, submission_id, run_data):
    """
    Update information for a workflow run.
    """
    evals = _get_evals()
    evals[eval_id][submission_id]['run'] = run_data
    _save_evals(evals)
