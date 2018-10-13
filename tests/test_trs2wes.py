import logging
import pytest
import mock
import yaml

from wfinterop.trs2wes import fetch_queue_workflow
from wfinterop.trs2wes import store_verification
from wfinterop.trs2wes import get_version
from wfinterop.trs2wes import get_wf_info

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def test_fetch_queue_workflow(mock_orchestratorqueues,
                              mock_queue_config, 
                              mock_trs, 
                              monkeypatch):
    monkeypatch.setattr('wfinterop.config.queues_path', 
                        str(mock_orchestratorqueues))
    monkeypatch.setattr('wfinterop.trs2wes.queue_config', 
                        lambda: mock_queue_config)
    monkeypatch.setattr('wfinterop.trs2wes.TRS', 
                        lambda trs_id: mock_trs)
    
    mock_trs.get_workflow_descriptor.return_value = {'url': 'mock_wf_url'}
    mock_trs.get_workflow_files.return_value = [{'file_type': 'SECONDARY_DESCRIPTOR',
                                                 'path': 'mock_path'}]
    mock_trs.get_workflow_descriptor_relative.return_value = {'url': 'mock_file_url'}

    fetch_queue_workflow('mock_queue_1')

    mock_config = {'workflow_id': 'mock_wf',
                   'version_id': 'develop',
                   'workflow_type': 'CWL',
                   'trs_id': 'mock_trs',
                   'workflow_url': 'mock_wf_url',
                   'workflow_attachments': ['mock_file_url'],
                   'wes_default': 'local',
                   'wes_opts': ['local'],
                   'target_queue': None}

    with open(str(mock_orchestratorqueues), 'r') as f:
        test_config = yaml.load(f)

    assert(test_config['mock_queue_1'] == mock_config)


def test_store_verification(mock_orchestratorqueues, 
                            mock_queue_config, 
                            monkeypatch):
    # GIVEN an orchestrator config file exists
    monkeypatch.setattr('wfinterop.config.queues_path', 
                        str(mock_orchestratorqueues))
    monkeypatch.setattr('wfinterop.config.queue_config', 
                        lambda: mock_queue_config)
    
    # WHEN an evaluation queue is added to the configuration of the
    # workflow orchestrator app
    store_verification(
        queue_id='mock_queue_1',
        wes_id='mock_wes'
    )

    mock_config = {'trs_id': 'mock_trs',
                   'workflow_id': 'mock_wf',
                   'version_id': 'develop',
                   'workflow_type': 'CWL',
                   'workflow_url': None,
                   'workflow_attachments': None,
                   'wes_default': 'local',
                   'wes_opts': ['local'],
                   'target_queue': None,
                   'wes_verified': ['mock_wes']}

    # THEN the evaluation queue config should be stored in the config file
    with open(str(mock_orchestratorqueues), 'r') as f:
        test_config = yaml.load(f)

    assert(test_config['mock_queue_1'] == mock_config)


def test_get_version_cwl():
    test_version = get_version(extension='cwl',
                               workflow_file='tests/testdata/md5sum.cwl')
    assert test_version == 'v1.0'


def test_get_version_wdl():
    test_version = get_version(extension='wdl',
                               workflow_file='tests/testdata/md5sum.wdl')
    assert test_version == 'draft-2'


def test_get_wf_info_cwl():
    test_info = get_wf_info(workflow_path='tests/testdata/md5sum.cwl')
    assert test_info == ('v1.0', 'CWL')


def test_get_wf_info_wdl():
    test_info = get_wf_info(workflow_path='tests/testdata/md5sum.wdl')
    assert test_info == ('draft-2', 'WDL')