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
