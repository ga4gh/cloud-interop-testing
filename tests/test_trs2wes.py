import logging
import pytest
import mock
import yaml

from synorchestrator.trs2wes import fetch_queue_workflow

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def test_fetch_queue_workflow(mock_orchestratorconfig,
                              mock_queue_config, 
                              mock_trs, 
                              monkeypatch):
    monkeypatch.setattr('synorchestrator.config.config_path', 
                        str(mock_orchestratorconfig))
    monkeypatch.setattr('synorchestrator.trs2wes.queue_config', 
                        lambda: mock_queue_config)
    monkeypatch.setattr('synorchestrator.trs2wes.TRS', 
                        lambda trs_id: mock_trs)
    
    mock_trs.get_workflow_descriptor.return_value = {'url': 'mock_wf_url'}
    mock_trs.get_workflow_files.return_value = [{'url': 'mock_file_url'}]

    fetch_queue_workflow('mock_queue_1')

    mock_config = {'workflow_id': 'mock_wf',
                   'version_id': 'develop',
                   'workflow_type': '',
                   'trs_id': 'mock_trs',
                   'workflow_url': 'mock_wf_url',
                   'workflow_attachments': ['mock_file_url'],
                   'wes_default': 'local',
                   'wes_opts': ['local']}

    with open(str(mock_orchestratorconfig), 'r') as f:
        test_config = yaml.load(f)['queues']

    assert(test_config['mock_queue_1'] == mock_config)