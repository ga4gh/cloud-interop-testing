import logging
import mock
import pytest
import yaml

from wfinterop.config import queue_config
from wfinterop.config import trs_config
from wfinterop.config import wes_config
from wfinterop.config import add_queue
from wfinterop.config import add_toolregistry
from wfinterop.config import add_workflowservice
from wfinterop.config import set_yaml
from wfinterop.config import show

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def test_queue_config(mock_orchestratorqueues, mock_queue_config, monkeypatch):
    # GIVEN an orchestrator config file exists
    monkeypatch.setattr('wfinterop.config.queues_path', 
                        str(mock_orchestratorqueues))

    # WHEN the configuration data in the file is loaded
    test_config = queue_config()

    # THEN the returned object is correctly parsed from the YAML stream
    assert(test_config == mock_queue_config)


def test_trs_config(mock_orchestratorconfig, mock_trs_config, monkeypatch):
    # GIVEN an orchestrator config file exists
    monkeypatch.setattr('wfinterop.config.config_path', 
                        str(mock_orchestratorconfig))
    
    # WHEN the configuration data in the file is loaded
    test_config = trs_config()

    # THEN the returned object is correctly parsed from the YAML stream
    assert(test_config == mock_trs_config)


def test_wes_config(mock_orchestratorconfig, mock_wes_config, monkeypatch):
    # GIVEN an orchestrator config file exists
    monkeypatch.setattr('wfinterop.config.config_path', 
                        str(mock_orchestratorconfig))
    
    # WHEN the configuration data in the file is loaded
    test_config = wes_config()

    # THEN the returned object is correctly parsed from the YAML stream
    assert(test_config == mock_wes_config)


def test_add_queue(mock_orchestratorqueues, monkeypatch):
    # GIVEN an orchestrator config file exists
    monkeypatch.setattr('wfinterop.config.queues_path', 
                        str(mock_orchestratorqueues))
    
    # WHEN an evaluation queue is added to the configuration of the
    # workflow orchestrator app
    add_queue(
        queue_id='mock_queue',
        wf_type='',
        wf_id='mock_wf',
        version_id='develop'
    )

    mock_config = {'workflow_type': '',
                   'trs_id': 'dockstore',
                   'workflow_id': 'mock_wf',
                   'version_id': 'develop',
                   'workflow_url': None,
                   'workflow_attachments': None,
                   'wes_default': 'local',
                   'wes_opts': ['local'],
                   'target_queue': None}

    # THEN the evaluation queue config should be stored in the config file
    with open(str(mock_orchestratorqueues), 'r') as f:
        test_config = yaml.load(f)

    assert('mock_queue' in test_config)
    assert(test_config['mock_queue'] == mock_config)


def test_add_toolregistry(mock_orchestratorconfig, monkeypatch):
    # GIVEN an orchestrator config file exists
    monkeypatch.setattr('wfinterop.config.config_path', 
                        str(mock_orchestratorconfig))

    # WHEN a TRS endpoint is added to the configuration of the
    # workflow orchestrator app
    add_toolregistry(
        service='mock_trs',
        auth='',
        host='',
        proto=''
    )

    mock_config = {'auth': '',
                   'host': '',
                   'proto': ''}

    # THEN the TRS config should be stored in the config file
    with open(str(mock_orchestratorconfig), 'r') as f:
        test_config = yaml.load(f)['toolregistries']

    assert('mock_trs' in test_config)
    assert(test_config['mock_trs'] == mock_config)


def test_add_workflowservice(mock_orchestratorconfig, monkeypatch):
    # GIVEN an orchestrator config file exists
    monkeypatch.setattr('wfinterop.config.config_path', 
                        str(mock_orchestratorconfig))
    
    # WHEN a WES endpoint is added to the configuration of the
    # workflow orchestrator app
    add_workflowservice(
        service='mock_wes',
        auth='',
        host='',
        proto=''
    )

    mock_config = {'auth': '',
                   'host': '',
                   'proto': ''}

    # THEN the WES config should be stored in the config file
    with open(str(mock_orchestratorconfig), 'r') as f:
        test_config = yaml.load(f)['workflowservices']

    assert('mock_wes' in test_config)
    assert(test_config['mock_wes'] == mock_config)


def test_set_yaml(mock_orchestratorconfig, monkeypatch):
    # GIVEN an orchestrator config file exists
    monkeypatch.setattr('wfinterop.config.config_path', 
                        str(mock_orchestratorconfig))
    
    # WHEN the config is set for a given section and service
    set_yaml(
        section='mock_section',
        service='mock_service',
        var2add={}
    )

    # THEN the config should be stored under the correct section and service
    with open(str(mock_orchestratorconfig), 'r') as f:
        test_config = yaml.load(f)

    assert('mock_section' in test_config)
    assert('mock_service' in test_config['mock_section'])
    assert(test_config['mock_section']['mock_service'] == {})
