"""
The orchestrator config file has three sections: eval, trs, and wes.

This provides functions to save and get values into these three sections in the file.
"""
import logging
import os
from synorchestrator.util import get_yaml, save_yaml, heredoc

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


config_path = os.path.join(os.path.dirname(__file__), 'config.yaml')


def queue_config():
    return get_yaml(config_path)['queues']


def trs_config():
    return get_yaml(config_path)['toolregistries']


def wes_config():
    return get_yaml(config_path)['workflowservices']


def add_queue(wf_id,
              version_id,
              wf_type,
              queue_name=None,
              trs_id='dockstore',
              wes_default='local',
              wes_opts=None):
    """
    Register a Synapse evaluation queue to the orchestrator's
    scope of work.

    :param eval_id: integer ID of a Synapse evaluation queue
    """
    if queue_name is None:
        queue_name = '{}__{}'.format(os.path.basename(wf_id), version_id)
    wes_opts = [wes_default] if wes_opts is None else wes_opts
    config = {'workflow_id': wf_id,
              'version_id': version_id,
              'workflow_type': wf_type,
              'trs_id': trs_id,
              'wes_default': wes_default,
              'wes_opts': wes_opts}
    set_yaml('queues', queue_name, config)


def add_toolregistry(service, auth, auth_type, host, proto):
    """
    Register a Tool Registry Service endpoint to the orchestrator's
    search space for workflows.

    :param trs_id: string ID of TRS endpoint (e.g., 'Dockstore')
    """
    config = {'auth': auth,
              'auth_type': auth,
              'host': host,
              'proto': proto}
    set_yaml('toolregistries', service, config)


def add_workflowservice(service, auth, auth_type, host, proto):
    """
    Register a Workflow Execution Service endpoint to the
    orchestrator's available environment options.

    :param wes_id: string ID of WES endpoint (e.g., 'workflow-service')
    """
    config = {'auth': auth,
              'auth_type': auth_type,
              'host': host,
              'proto': proto}
    set_yaml('workflowservices', service, config)


def set_yaml(section, service, var2add):
    orchestrator_config = get_yaml(config_path)
    orchestrator_config.setdefault(section, {})[service] = var2add
    save_yaml(config_path, orchestrator_config)


def show():
    """
    Show current application configuration.
    """
    orchestrator_config = get_yaml(config_path)
    workflows = '\n'.join('{}:\t{}\t[{}]'.format(k, orchestrator_config['queues'][k]['workflow_id'], orchestrator_config['queues'][k]['workflow_type']) for k in orchestrator_config['queues'])
    trs = '\n'.join('{}: {}'.format(k, orchestrator_config['toolregistries'][k]['host']) for k in orchestrator_config['toolregistries'])
    wes = '\n'.join('{}: {}'.format(k, orchestrator_config['workflowservices'][k]['host']) for k in orchestrator_config['workflowservices'])
    display = heredoc('''
        Orchestrator options:

        Workflow Evaluation Queues
        (queue ID: workflow ID [workflow type])
        ---------------------------------------------------------------------------
        {evals}

        Tool Registries
        (TRS ID: host address)
        ---------------------------------------------------------------------------
        {trs}

        Workflow Services
        (WES ID: host address)
        ---------------------------------------------------------------------------
        {wes}
        ''', {'evals': evals,
              'trs': trs,
              'wes': wes})
    print(display)
