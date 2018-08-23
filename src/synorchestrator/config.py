"""
The orchestrator config file has three sections: eval, trs, and wes.

This provides functions to save and get values into these three sections in the file.
"""
import logging
import os

from synorchestrator.util import get_json, save_json, heredoc

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Config():

    def __init__(self, config_loc=""):
        self.config_loc = self._create_config(config_loc)

    def _create_config(self, given=""):
        """
        Create a config file if one does not exist.

        This method's name is somewhat of a misnomer. This method abstracts the checking for the file away from the init.
        It will only create the config file if it does not already exist. This allows the user the specify a location
        in the init which could point to an existing file or the location where they want a new one to be created.
        """
        config_loc = given or os.path.join(os.path.expanduser('~'), 'orchestrator_config.json')
        if not os.path.exists(config_loc):
            with open(config_loc, 'w') as f:
                f.write('{"workflows": {},\n'
                        ' "toolregistries": {},\n'
                        ' "workflowservices": {}'
                        '}\n')
        return config_loc

    @property
    def config_path(self):
        return self.config_loc

    def wf_config(self):
        return get_json(self.config_path)['workflows']

    def trs_config(self):
        return get_json(self.config_path)['toolregistries']

    def wes_config(self):
        return get_json(self.config_path)['workflowservices']

    def add_workflow(self,
                     wf_name,
                     wf_type,
                     wf_url,
                     wf_attachments,
                     submission_type='params',
                     trs_id='dockstore',
                     version_id='develop'):
        """
        Register a Synapse evaluation queue to the orchestrator's
        scope of work.

        :param eval_id: integer ID of a Synapse evaluation queue
        """
        config = {'submission_type': submission_type,
                  'trs_id': trs_id,
                  'version_id': version_id,
                  'workflow_type': wf_type,
                  'workflow_url': wf_url,
                  'workflow_attachments': wf_attachments}
        self.set_json('workflows', wf_name, config)


    def add_toolregistry(self, service, auth, host, proto):
        """
        Register a Tool Registry Service endpoint to the orchestrator's
        search space for workflows.

        :param trs_id: string ID of TRS endpoint (e.g., 'Dockstore')
        """
        config = {'auth': auth,
                  'host': host,
                  'proto': proto}
        self.set_json('toolregistries', service, config)

    def add_workflowservice(self, service, auth, client, host, proto):
        """
        Register a Workflow Execution Service endpoint to the
        orchestrator's available environment options.

        :param wes_id: string ID of WES endpoint (e.g., 'workflow-service')
        """
        config = {'auth': auth,
                  'host': host,
                  'proto': proto,
                  'client': client}
        self.set_json('workflowservices', service, config)

    def set_json(self, section, service, var2add):
        try:
            orchestrator_config = get_json(self.config_path)
            orchestrator_config.setdefault(section, {})[service] = var2add
            save_json(self.config_path, orchestrator_config)
        except AttributeError:
            raise AttributeError('The config file needs to be set: ' + self.config_path)

    def show(self):
        """
        Show current application configuration.
        """
        orchestrator_config = get_json(self.config_path)
        wfs = '\n'.join('{}\t[{}]'.format(k, orchestrator_config['workflows'][k]['workflow_type']) for k in orchestrator_config['workflows'])
        trs = '\n'.join('{}:\t{}'.format(k, orchestrator_config['toolregistries'][k]['host']) for k in orchestrator_config['toolregistries'])
        wes = '\n'.join('{}:\t{}'.format(k, orchestrator_config['workflowservices'][k]['host']) for k in orchestrator_config['workflowservices'])
        display = heredoc('''
            Orchestrator Options:
    
            Parametrized Workflows
            (Workflow Name [Workflow Type])
            ---------------------------------------------------------------------------
            {wfs}
    
            Tool Registries
            (TRS ID: Host Address)
            ---------------------------------------------------------------------------
            {trs}
    
            Workflow Services
            (WES ID: Host Address)
            ---------------------------------------------------------------------------
            {wes}
            ''', {'wfs': wfs,
                  'trs': trs,
                  'wes': wes})
        print(display)
