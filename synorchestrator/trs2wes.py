# from wes_client.util import build_wes_request
# from wes_client.util import modify_jsonyaml_path
# from wes_client.util import expand_globs

from synorchestrator.config import config_path
from synorchestrator.config import queue_config
from synorchestrator.config import set_yaml
from synorchestrator.trs.wrapper import TRS


def fetch_queue_workflow(queue_name):
    wf_config = queue_config()[queue_name]
    trs_instance = TRS(wf_config['trs_id'])
    wf_descriptor = trs_instance.get_workflow_descriptor(
        id=wf_config['workflow_id'],    
        version_id=wf_config['version_id'], 
        type=wf_config['workflow_type']
    )
    wf_files = trs_instance.get_workflow_files(
        id=wf_config['workflow_id'],
        version_id=wf_config['version_id'],
        type=wf_config['workflow_type']
    )
    wf_config['workflow_url'] = wf_descriptor['url']
    wf_config['workflow_attachments'] = [wf_file['url']
                                         for wf_file in wf_files]
    set_yaml('queues', queue_name, wf_config)

    