#!/usr/bin/env python


def add_queue(opts):
    """
    Register a Synapse evaluation queue to the orchestrator's
    scope of work.
    """
    pass

def add_toolregistry(opts):
    """
    Register a Tool Registry Service endpoint to the orchestrator's
    search space for workflows.
    """
    pass

def add_workflowservice(opts):
    """
    Register a Workflow Execution Service endpoint to the
    orchestrator's available environment options.
    """
    pass

def run_submission(queue_id, submission_id, wes_id):
    """
    For a single submission to a single evaluation queue, run
    the workflow in a single environment.
    """
    pass

def run_queue(queue_id, wes_id):
    """
    Run all submissions in a queue in a single environment.
    """
    pass

def run_all(queue_ids, wes_ids):
    """
    Run all submissions for multiple queues in multiple environments
    (cross product of queues, workflow service endpoints).
    """
    pass
