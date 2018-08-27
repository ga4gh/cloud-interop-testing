import logging
import pytest
import mock
import yaml
import textwrap

from synorchestrator.trs2wes import fetch_queue_workflow

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


@pytest.fixture(scope='function')
def mock_orchestratorconfig(tmpdir):
    # a mocked config file for a the orchestrator app
    logger.info("[setup] mock orchestrator config file, create local file")

    mock_config_text = """
    queues:
      mock_wf__develop: {}
      wf2: {}

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


@pytest.fixture()
def mock_queue_config():
    mock_queue_config = {
        'mock_wf__develop': {
            'trs_id': 'mock_trs',
            'workflow_id': 'mock_wf',
            'version_id': 'develop',
            'workflow_type': '',
            'wes_default': 'local',
            'wes_opts': ['local']
        },
        'mock_wf__prod': {
            'trs_id': 'mock_trs',
            'workflow_id': 'mock_wf',
            'version_id': 'prod',
            'workflow_type': '',
            'wes_default': 'local',
            'wes_opts': ['local']
        }
    }
    yield mock_queue_config


@pytest.fixture()
def mock_trs(request):
    mock_trs = mock.Mock(name='mock TRS')
    with mock.patch('synorchestrator.trs.wrapper.TRS', 
                    autospec=True, spec_set=True):
        yield mock_trs


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

    fetch_queue_workflow('mock_wf__develop')

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

    assert(test_config['mock_wf__develop'] == mock_config)