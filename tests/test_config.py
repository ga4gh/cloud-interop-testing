import logging
# import os
import pytest
import yaml
import textwrap

from synorchestrator import config

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


@pytest.fixture(scope='function')
def mock_orchestratorconfig(tmpdir):
    # a mocked config file for a the orchestrator app
    logger.info("[setup] mock orchestrator config file, create local file")

    mock_config_text = """
    evals:
      eval1: {}
      eval2: {}

    toolregistries:
      trs1: {}
      trs2: {}

    workflowservices:
      wes1: {}
      wes2: {}
    """
    mock_config_file = tmpdir.join('config.yaml')
    logger.debug("writing config file: {}".format(str(mock_config_file)))
    mock_config_file.write(textwrap.dedent(mock_config_text))

    yield mock_config_file

    logger.info("[teardown] mock orchestrator config file, remove file")


def test_eval_config(mock_orchestratorconfig, monkeypatch):
    # GIVEN an orchestrator config file exists
    monkeypatch.setattr(config, 'config_path', str(mock_orchestratorconfig))


    # WHEN the configuration data in the file is loaded
    test_config = config.eval_config()

    # THEN the returned object is correctly parsed from the YAML stream
    assert(
        test_config == {
            'eval1': {},
            'eval2': {}
        }
    )


def test_trs_config(mock_orchestratorconfig, monkeypatch):
    # GIVEN an orchestrator config file exists
    monkeypatch.setattr(config, 'config_path', str(mock_orchestratorconfig))

    # WHEN the configuration data in the file is loaded
    test_config = config.trs_config()

    # THEN the returned object is correctly parsed from the YAML stream
    assert(
        test_config == {
            'trs1': {},
            'trs2': {}
        }
    )


def test_wes_config(mock_orchestratorconfig, monkeypatch):
    # GIVEN an orchestrator config file exists
    monkeypatch.setattr(config, 'config_path', str(mock_orchestratorconfig))

    # WHEN the configuration data in the file is loaded
    test_config = config.wes_config()

    # THEN the returned object is correctly parsed from the YAML stream
    assert(
        test_config == {
            'wes1': {},
            'wes2': {}
        }
    )


def test_add_eval(mock_orchestratorconfig, monkeypatch):
    # GIVEN an orchestrator config file exists
    monkeypatch.setattr(config, 'config_path', str(mock_orchestratorconfig))

    # WHEN an evaluation queue is added to the configuration of the
    # workflow orchestrator app
    config.add_eval(
        wf_name='mock_wf',
        wf_type='',
        wf_url='',
        wf_jsonyaml='',
        wf_attachments=[]
    )

    mock_config = {'submission_type': 'params',
                   'trs_id': 'dockstore',
                   'version_id': 'develop',
                   'workflow_id': '',
                   'workflow_type': '',
                   'workflow_url': '',
                   'workflow_jsonyaml': '',
                   'workflow_attachments': []}

    # THEN the evaluation queue config should be stored in the config file
    with open(str(mock_orchestratorconfig), 'r') as f:
        test_config = yaml.load(f)['evals']

    assert('mock_wf' in test_config)
    assert(test_config['mock_wf'] == mock_config)


def test_add_toolregistry(mock_orchestratorconfig, monkeypatch):
    # GIVEN an orchestrator config file exists
    monkeypatch.setattr(config, 'config_path', str(mock_orchestratorconfig))

    # WHEN a TRS endpoint is added to the configuration of the
    # workflow orchestrator app
    config.add_toolregistry(
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
    monkeypatch.setattr(config, 'config_path', str(mock_orchestratorconfig))

    # WHEN a WES endpoint is added to the configuration of the
    # workflow orchestrator app
    config.add_workflowservice(
        service='mock_wes',
        auth='',
        auth_type='',
        host='',
        proto=''
    )

    mock_config = {'auth': '',
                   'auth_type': '',
                   'host': '',
                   'proto': ''}

    # THEN the WES config should be stored in the config file
    with open(str(mock_orchestratorconfig), 'r') as f:
        test_config = yaml.load(f)['workflowservices']

    assert('mock_wes' in test_config)
    assert(test_config['mock_wes'] == mock_config)


def test_set_yaml(mock_orchestratorconfig, monkeypatch):
    # GIVEN an orchestrator config file exists
    monkeypatch.setattr(config, 'config_path', str(mock_orchestratorconfig))

    # WHEN the config is set for a given section and service
    config.set_yaml(
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