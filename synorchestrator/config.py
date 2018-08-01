"""
The orchestrator config file has three sections: eval, trs, and wes.

This provides functions to save and get values into these three sections in the file.
"""
import logging
import os
from synorchestrator.util import get_yaml, save_yaml

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


orchestrator_filepath = os.path.abspath('config/orchestrator.config.yaml')
# eval_filepath = os.path.abspath('configs/evals.config.yaml')
# eval_config = get_yaml(eval_filepath)
# trs_filepath = os.path.abspath('configs/toolregistries.config.yaml')
# trs_config = get_yaml(trs_filepath)
# wes_filepath = os.path.abspath('configs/workflowservices.config.yaml')
# wes_config = get_yaml(wes_filepath)


def add_eval(eval_id):
    """
    Register a Synapse evaluation queue to the orchestrator's
    scope of work.

    :param eval_id: integer ID of a Synapse evaluation queue
    """
    set_yaml(section='evals', var2add=eval_id)


def add_toolregistry(trs_id):
    """
    Register a Tool Registry Service endpoint to the orchestrator's
    search space for workflows.

    :param trs_id: string ID of TRS endpoint (e.g., 'Dockstore')
    """
    set_yaml(section='toolregistries', var2add=trs_id)


def add_workflowservice(wes_id):
    """
    Register a Workflow Execution Service endpoint to the
    orchestrator's available environment options.

    :param wes_id: string ID of WES endpoint (e.g., 'workflow-service')
    """
    set_yaml(section='workflowservices', var2add=wes_id)


def set_yaml(section, var2add):
    orchestrator_config = get_yaml(orchestrator_filepath)
    orchestrator_config.setdefault(section, []).append(var2add)
    save_yaml(orchestrator_filepath, orchestrator_config)


def show():
    """
    Show current application configuration.
    """
    orchestrator_config = get_yaml(orchestrator_filepath)
    print("\nOrchestrator options:")
    print("\nWorkflow Evaluation Queues")
    print("(queue ID: workflow ID [workflow type])")
    print("-" * 75)
    print('\n'.join('{}: {} [{}]'.format(k,
                                         orchestrator_config['evals'][k]['workflow_id'],
                                         orchestrator_config['evals'][k]['workflow_type']) for k in orchestrator_config['evals']))
    print("\nTool Registries")
    print("(TRS ID: host address)")
    print("-" * 75)
    print('\n'.join('{}: {}'.format(k,
                                    orchestrator_config['toolregistries'][k]['host']) for k in orchestrator_config['toolregistries']))
    print("\nWorkflow Services")
    print("(WES ID: host address)")
    print("-" * 75)
    print('\n'.join('{}: {}'.format(k,
                                    orchestrator_config['workflowservices'][k]['host']) for k in orchestrator_config['workflowservices']))
