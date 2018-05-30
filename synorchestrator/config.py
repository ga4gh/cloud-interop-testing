"""
Configure orchestrator application.
"""
import logging
import os
import yaml
import pkg_resources

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CONFIG_PATH = os.path.join(os.path.expanduser('~'), '.orchestratorConfig')

with pkg_resources.resource_stream(__name__, 'configs/evals.config') as f:
    eval_config = yaml.load(f)
with pkg_resources.resource_stream(__name__, 'configs/toolregistries.config') as f:
    trs_config = yaml.load(f)
with pkg_resources.resource_stream(__name__, 'configs/workflowservices.config') as f:
    wes_config = yaml.load(f)


def _get_orchestrator_config():
    """
    Read orchestrator configuration from file.

    :return: object with current orchestrator app configuration
    """
    try:
        with open(CONFIG_PATH, 'r') as f:
            return yaml.load(f)
    except IOError as e:
        logger.warn("no orchestrator config file found")
        return {}


def _save_orchestrator_config(app_config):
    """
    Update orchestrator config file.
    """
    with open(CONFIG_PATH, 'w') as f:
        yaml.dump(app_config, f, default_flow_style=False)


def add_eval(eval_id):
    """
    Register a Synapse evaluation queue to the orchestrator's
    scope of work.

    :param eval_id: integer ID of a Synapse evaluation queue
    """
    app_config = _get_orchestrator_config()
    app_config.setdefault('evals', []).append(eval_id)
    _save_orchestrator_config(app_config)


def add_toolregistry(trs_id):
    """
    Register a Tool Registry Service endpoint to the orchestrator's
    search space for workflows.

    :param trs_id: string ID of TRS endpoint (e.g., 'Dockstore')
    """
    app_config = _get_orchestrator_config()
    app_config.setdefault('toolregistries', []).append(trs_id)
    _save_orchestrator_config(app_config)


def add_workflowservice(wes_id):
    """
    Register a Workflow Execution Service endpoint to the
    orchestrator's available environment options.

    :param wes_id: string ID of WES endpoint (e.g., 'workflow-service')
    """
    app_config = _get_orchestrator_config()
    app_config.setdefault('workflowservices', []).append(wes_id)
    _save_orchestrator_config(app_config)


def show():
    """
    Show current application configuration.
    """
    app_config = _get_orchestrator_config()
    print("\nOrchestrator options:")
    print("\nWorkflow Evaluation Queues")
    print("(queue ID: workflow ID [workflow type])")
    print("-" * 75)
    print(
        '\n'.join('{}: {} [{}]'.format(
            k, eval_config[k]['workflow_id'], eval_config[k]['workflow_type']
        )
        for k in app_config['evals'])
    )
    print("\nTool Registries")
    print("(TRS ID: host address)")
    print("-" * 75)
    print('\n'.join('{}: {}'.format(k, trs_config[k]['host'])
          for k in app_config['toolregistries']))
    print("\nWorkflow Services")
    print("(WES ID: host address)")
    print("-" * 75)
    print('\n'.join('{}: {}'.format(k, wes_config[k]['host'])
          for k in app_config['workflowservices']))
