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


def eval_config():
    return get_yaml(config_path)['evals']


def trs_config():
    return get_yaml(config_path)['toolregistries']


def wes_config():
    return get_yaml(config_path)['workflowservices']


def add_eval(wf_name,
             wf_type,
             wf_url,
             wf_jsonyaml,
             wf_attachments,
             submission_type='params',
             trs_id='dockstore',
             version_id='develop',
             wf_id=''):
    """
    Register a Synapse evaluation queue to the orchestrator's
    scope of work.

    :param eval_id: integer ID of a Synapse evaluation queue
    """
    config = {'submission_type': submission_type,
              'trs_id': trs_id,
              'version_id': version_id,
              'workflow_id': wf_id,
              'workflow_type': wf_type,
              'workflow_url': wf_url,
              'workflow_jsonyaml': wf_jsonyaml,
              'workflow_attachments': wf_attachments}
    print(config)
    print(wf_name)
    set_yaml('evals', wf_name, config)


def add_toolregistry(service, auth, host, proto):
    """
    Register a Tool Registry Service endpoint to the orchestrator's
    search space for workflows.

    :param trs_id: string ID of TRS endpoint (e.g., 'Dockstore')
    """
    config = {'auth': auth,
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
    print(orchestrator_config)
    orchestrator_config.setdefault(section, {})[service] = var2add
    save_yaml(config_path, orchestrator_config)


def show():
    """
    Show current application configuration.
    """
    orchestrator_config = get_yaml(config_path)
    evals = '\n'.join('{}:\t{}\t[{}]'.format(k, orchestrator_config['evals'][k]['workflow_id'], orchestrator_config['evals'][k]['workflow_type']) for k in orchestrator_config['evals'])
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


add_eval(wf_name='wdl_UoM_align',
         wf_type='WDL',
         wf_url='/home/quokka/Desktop/topmed-workflows/aligner/u_of_michigan_aligner/u_of_michigan_aligner.wdl',
         wf_jsonyaml='file:///home/quokka/Desktop/topmed-workflows/aligner/u_of_michigan_aligner/u_of_michigan_aligner.json',
         wf_attachments=[])
