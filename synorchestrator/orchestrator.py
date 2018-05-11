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
import yaml

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

CONFIG_FILE = os.path.join(os.path.expanduser('~'), '.orchestratorConfig')


def _get_orchestrator_config():
    """
    Read orchestrator configuration from file.

    :return: object with current orchestrator app configuration
    """
    try:
        logger.debug("loading orchestrator config from {}".format(CONFIG_FILE))
        with open(CONFIG_FILE, 'r') as f:
            return yaml.load(f)
    except IOError as e:
        logger.warn("no orchestrator config file found")
        return {}


def _save_orchestrator_config(config):
    """
    Update orchestrator config file.
    """
    with open(CONFIG_FILE, 'w') as f:
        yaml.dump(config, f, default_flow_style=False)


def add_eval(eval_id):
    """
    Register a Synapse evaluation queue to the orchestrator's
    scope of work.

    :param eval_id: integer ID of a Synapse evaluation queue
    """
    config = _get_orchestrator_config()
    config.setdefault('evals', []).append(eval_id)
    _save_orchestrator_config(config)


def add_toolregistry(trs_id):
    """
    Register a Tool Registry Service endpoint to the orchestrator's
    search space for workflows.

    :param trs_id: string ID of TRS endpoint (e.g., 'Dockstore')
    """
    config = _get_orchestrator_config()
    config.setdefault('toolregistries', []).append(trs_id)
    _save_orchestrator_config(config)


def add_workflowservice(wes_id):
    """
    Register a Workflow Execution Service endpoint to the
    orchestrator's available environment options.

    :param wes_id: string ID of WES endpoint (e.g., 'workflow-service')
    """
    config = _get_orchestrator_config()
    config.setdefault('workflowservices', []).append(wes_id)
    _save_orchestrator_config(config)


def run_submission(eval_id, submission_id, wes_id):
    """
    For a single submission to a single evaluation queue, run
    the workflow in a single environment.
    """
    pass


def run_eval(eval_id, wes_id):
    """
    Run all submissions in a queue in a single environment.
    """
    pass


def run_all(eval_ids, wes_ids):
    """
    Run all submissions for multiple queues in multiple environments
    (cross product of queues, workflow service endpoints).
    """
    pass
