#!/usr/bin/env python
"""
The orchestrator config has three sections for workflow queues, tool
registry services (TRS), and workflow execution services (WES). The latter
two sections are stored in the same file, and individual entries are
generally unchanged after adding. The former (queues) are stored in a
separate file.

This provides functions to save and get values into these three sections.
"""
import logging
import os

from ga4ghtest.util import get_yaml, save_yaml, heredoc

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _default_queues():
    """
    Create default queues config file with example workflow data.
    """
    queues = {
        'test_cwl_queue': {
            'target_queue': None,
            'trs_id': None,
            'version_id': None,
            'wes_default': 'local',
            'wes_opts': ['local'],
            'workflow_attachments': [
                'file://tests/testdata/md5sum.input',
                'file://tests/testdata/dockstore-tool-md5sum.cwl'],
            'workflow_id': None,
            'workflow_type': 'CWL',
            'workflow_url': 'file://tests/testdata/md5sum.cwl'},
        'test_wdl_queue': {
            'target_queue': None,
            'trs_id': None,
            'version_id': None,
            'wes_default': 'local',
            'wes_opts': ['local'],
            'workflow_attachments': ['file://tests/testdata/md5sum.input'],
            'workflow_id': None,
            'workflow_type': 'WDL',
            'workflow_url': 'file://tests/testdata/md5sum.wdl'}
    }
    save_yaml(queues_path, queues)


def _default_config():
    """
    Create default app config, if not existing.
    """
    config = {
        'toolregistries': {
            'dockstore': {
                'auth': {'Authorization': ''},
                'host': 'dockstore.org:8443',
                'proto': 'https'}},
        'workflowservices': {
            'local': {
                'auth': {'Authorization': ''},
                'host': '0.0.0.0:8080',
                'proto': 'http'}}}
    save_yaml(config_path, config)


config_path = os.path.join(os.path.dirname(__file__), 'config.yaml')
if not os.path.exists(config_path):
    _default_config()

queues_path = os.path.join(os.path.dirname(__file__), 'queues.yaml')
if not os.path.exists(queues_path):
    _default_queues()


def add_queue(queue_id,
              wf_type,
              trs_id='dockstore',
              wf_id=None,
              version_id='local',
              wf_url=None,
              wf_attachments=None,
              wes_default='local',
              wes_opts=None,
              target_queue=None):
    """
    Register a workflow evaluation queue to the orchestrator's
    scope of work.

    Args:
        queue_id (str): string identifying the workflow queue
        wf_type (str): string indicating the workflow type (e.g.,
            'CWL' or 'WDL')
        wf_id (str): string representing the workflow ID as registered
            in a tool registry service
        version_id (str): string denoting the version (as listed in the
            tool registry service) of the workflow to use.
        wf_url (str): string giving the full URL path to the main
            workflow descriptor file
        wf_attachments (:obj:`list` of :obj:`str`): filepaths or URLs to
            any additional workflow dependencies that should be attached
            at runtime
        wes_default (str): string corresponding to a workflow execution
            service in the app config.
        wes_opts (:obj:`list` of :obj:`str`): list of compatible workflow
            execution services to use for running the workflow.
        target_queue (str): string identifying the queue of the 'parent'
            workflow, if the current queue is designed to check/validate
            the parent.
    """
    if not wf_id and not wf_url:
        raise ValueError(
            "One of either 'wf_id' or 'wf_url' must be specified.")

    wes_opts = [wes_default] if wes_opts is None else wes_opts
    config = {'workflow_type': wf_type,
              'trs_id': trs_id,
              'workflow_id': wf_id,
              'version_id': version_id,
              'workflow_url': wf_url,
              'workflow_attachments': wf_attachments,
              'wes_default': wes_default,
              'wes_opts': wes_opts,
              'target_queue': target_queue}
    set_yaml('queues', queue_id, config)


def queue_config():
    """
    Fetch config data for workflow queues.

    Returns:
        dict: dict with an entry for each workflow queue
    """
    return get_yaml('file://' + queues_path)


def trs_config():
    """
    Fetch config data for tool registry services.

    Returns:
        dict: dict with an entry for each service
    """
    return get_yaml('file://' + config_path)['toolregistries']


def wes_config():
    """
    Fetch config data for workflow execution services.

    Returns:
        dict: dict with an entry for each service
    """
    return get_yaml('file://' + config_path)['workflowservices']

def add_toolregistry(service,
                     host,
                     auth={'Authorization': ''},
                     proto='https'):
    """
    Register a Tool Registry Service endpoint to the orchestrator's
    search space for workflows.

    Args:
        service (str): string ID of TRS endpoint (e.g., 'dockstore')
        host (str): domain and API path for endpoint
        auth (dict): dict with headers/tokens to use when authorizing
            requests to the API endpoint
        proto (str): protocol used by the API endpoint (e.g., http or https)
    """
    config = {'auth': auth,
              'host': host,
              'proto': proto}
    set_yaml('toolregistries', service, config)


def add_workflowservice(service,
                        host,
                        auth={'Authorization': ''},
                        proto='https'):
    """
    Register a Workflow Execution Service endpoint to the
    orchestrator's available environment options.

    Args:
        service (str): string ID of WES endpoint (e.g., 'local')
        host (str): domain and API path for endpoint
        auth (dict): dict with headers/tokens to use when authorizing
            requests to the API endpoint
        proto (str): protocol used by the API endpoint (e.g., http or https)
    """
    config = {'auth': auth,
              'host': host,
              'proto': proto}
    set_yaml('workflowservices', service, config)


def add_wes_opt(queue_ids, wes_id, make_default=False):
    """
    Add a WES endpoint to the execution options of the specified
    workflow queues.

    Args:
        queue_id (str): string identifying the workflow queue
        wes_id (str): string identifying the workflow execution service
        make_default (bool): True to make specified WES the new default
            for the workflow queue(s) or else False
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
    """
    Update data for a particular section or service in local
    YAML config files.

    Args:
        section (str): string indicating config type ('queues',
            'toolregistries', 'workflowservices')
        service (str): string identifying the service or queue
            to update
        var2add (dict): dict containing latest data for a service
            or queue (previous config will be overwritten)
    """
    if section == 'queues':
        orchestrator_queues = get_yaml('file://' + queues_path)
        orchestrator_queues[service] = var2add
        save_yaml(queues_path, orchestrator_queues)
    else:
        orchestrator_config = get_yaml('file://' + config_path)
        orchestrator_config.setdefault(section, {})[service] = var2add
        save_yaml(config_path, orchestrator_config)


def show():
    """
    Show current application configuration.
    """
    orchestrator_config = get_yaml(config_path)
    orchestrator_queues = get_yaml(queues_path)
    queue_lines = []
    for queue_id in orchestrator_queues:
        wf_config = orchestrator_queues[queue_id]
        wf_id = wf_config['workflow_id']
        version_id = wf_config['version_id']
        wf_url = wf_config['workflow_url']
        queue_attach = wf_config['workflow_attachments']
        if queue_attach:
            wf_attachments = '\n    - {}'.format(
                '\n    - '.join(queue_attach)
            )
        else:
            wf_attachments = queue_attach
        wf_type = wf_config['workflow_type']
        wf_trs = wf_config['trs_id']
        wf_wes_opts = wf_config['wes_opts']
        queue_lines.append(
            ('{}: {} ({})\n'
             '  > workflow URL: {}\n'
             '  > workflow attachments: {}\n'
             '  > workflow type: {}\n'
             '  > from TRS: {}\n'
             '  > WES options: {}').format(
                 queue_id,
                 wf_id,
                 version_id,
                 wf_url,
                 wf_attachments,
                 wf_type,
                 wf_trs,
                 wf_wes_opts
            )
        )

    queues = '\n'.join(queue_lines)
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
