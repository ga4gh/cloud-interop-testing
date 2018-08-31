"""
The orchestrator config file has three sections: queues, trs, and wes.

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


def add_queue(queue_id,
              wf_type,
              trs_id='dockstore',
              wf_id=None,
              version_id='local',
              wf_url=None,
              wf_attachments=None,
              wes_default='local',
              wes_opts=None):
    """
    Register a workflow evaluation queue to the orchestrator's
    scope of work.
    """
    if not wf_id and not wf_url:
        raise ValueError("One of either 'wf_id' or 'wf_url' must be specified.")

    wes_opts = [wes_default] if wes_opts is None else wes_opts
    config = {'workflow_type': wf_type,
              'trs_id': trs_id,
              'workflow_id': wf_id,
              'version_id': version_id,
              'workflow_url': wf_url,
              'workflow_attachments': wf_attachments,
              'wes_default': wes_default,
              'wes_opts': wes_opts}
    set_yaml('queues', queue_id, config)


def add_toolregistry(service, auth, auth_type, host, proto):
    """
    Register a Tool Registry Service endpoint to the orchestrator's
    search space for workflows.

    :param trs_id: string ID of TRS endpoint (e.g., 'dockstore')
    """
    config = {'auth': auth,
              'auth_type': auth,
              'host': host,
              'proto': proto}
    set_yaml('toolregistries', service, config)


def add_workflowservice(service, host, auth=None, auth_type=None, proto='https'):
    """
    Register a Workflow Execution Service endpoint to the
    orchestrator's available environment options.

    :param wes_id: string ID of WES endpoint (e.g., 'local')
    """
    config = {'auth': auth,
              'auth_type': auth_type,
              'host': host,
              'proto': proto}
    set_yaml('workflowservices', service, config)


def add_wes_opt(queue_ids, wes_id, make_default=False):
    """
    Add a WES endpoint to the execution options of the specified
    workflow queues.
    """
    if not isinstance(queue_ids, list):
        queue_ids = [queue_ids]
    for queue_id in queue_ids:
        wf_config = queue_config()[queue_id]
        wf_config['wes_opts'].append(wes_id)
        if make_default:
            wf_config['wes_default'] = wes_id
        set_yaml('queues', queue_id, wf_config)


def set_yaml(section, service, var2add):
    orchestrator_config = get_yaml(config_path)
    orchestrator_config.setdefault(section, {})[service] = var2add
    save_yaml(config_path, orchestrator_config)


def show():
    """
    Show current application configuration.
    """
    orchestrator_config = get_yaml(config_path)
    queues = '\n'.join(
        ('{}: {} ({})\n'
         '  > workflow URL: {}\n'
         '  > workflow type: {}\n'
         '  > from TRS: {}\n'
         '  > WES options: {}').format(
            k, 
            orchestrator_config['queues'][k]['workflow_id'],
            orchestrator_config['queues'][k]['version_id'],
            orchestrator_config['queues'][k]['workflow_url'],
            orchestrator_config['queues'][k]['workflow_type'],
            orchestrator_config['queues'][k]['trs_id'],
            orchestrator_config['queues'][k]['wes_opts']
        ) 
        for k in orchestrator_config['queues']
    )
    trs = '\n'.join('{}: {}'.format(
        k, 
        orchestrator_config['toolregistries'][k]['host']) 
        for k in orchestrator_config['toolregistries']
    )
    wes = '\n'.join('{}: {}'.format(
        k, 
        orchestrator_config['workflowservices'][k]['host']) 
        for k in orchestrator_config['workflowservices']
    )
    display = heredoc('''
        Orchestrator options:

        Workflow Evaluation Queues
        (queue ID: workflow ID [version])
        ---------------------------------------------------------------------------
        {queues}

        Tool Registries
        (TRS ID: host address)
        ---------------------------------------------------------------------------
        {trs}

        Workflow Services
        (WES ID: host address)
        ---------------------------------------------------------------------------
        {wes}
        ''', {'queues': queues,
              'trs': trs,
              'wes': wes})
    print(display)
