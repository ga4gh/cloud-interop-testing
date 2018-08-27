import logging
import pytest
import mock
import yaml

from bravado.client import SwaggerClient, ResourceDecorator


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

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
def mock_trs_config():
    mock_trs_config = {
        'mock_trs': {
            'auth': 'auth_token',
            'auth_type': 'token',
            'host': '0.0.0.0:8080',
            'proto': 'https'
        }
    }
    yield mock_trs_config


@pytest.fixture()
def mock_wes_config():
    mock_wes_config = {
        'mock_wes': {
            'auth': 'auth_token',
            'auth_type': 'token',
            'host': '0.0.0.0:8080',
            'proto': 'https'
        }
    }
    yield mock_wes_config


@pytest.fixture(scope='function')
def mock_orchestratorconfig(tmpdir, 
                            mock_queue_config, 
                            mock_trs_config, 
                            mock_wes_config):
    # a mocked config file for a the orchestrator app
    logger.info("[setup] mock orchestrator config file, create local file")

    mock_config = {'queues': mock_queue_config,
                   'toolregistries': mock_trs_config,
                   'workflowservices': mock_wes_config}
    mock_config_file = tmpdir.join('config.yaml')
    logger.debug("writing config file: {}".format(str(mock_config_file)))
    mock_config_file.write(yaml.dump(mock_config, default_flow_style=False))

    yield mock_config_file


@pytest.fixture()
def mock_client_lib(request):
    mock_wes_client = mock.Mock(name='mock WESClient')
    with mock.patch('wes_client.util.WESClient', 
                    autospec=True, spec_set=True):
        yield mock_wes_client


@pytest.fixture()
def mock_trs_client():
    mock_api_client = mock.Mock(name='mock SwaggerClient')
    with mock.patch.object(SwaggerClient, 'from_spec', 
                        return_value=mock_api_client):
        yield mock_api_client


@pytest.fixture(params=[None, 'workflow-service'])
def mock_wes_client(request):
    if request.param is None:
        mock_api_client = mock.Mock(name='mock SwaggerClient')
        with mock.patch.object(SwaggerClient, 'from_spec', 
                            return_value=mock_api_client):
            yield mock_api_client
    else:
        mock_api_client = mock.Mock(name='mock WESAdapter')
        with mock.patch('synorchestrator.wes.client.WESAdapter', 
                        autospec=True):
            yield mock_api_client


@pytest.fixture()
def mock_trs(request):
    mock_trs = mock.Mock(name='mock TRS')
    with mock.patch('synorchestrator.trs.wrapper.TRS', 
                    autospec=True, spec_set=True):
        yield mock_trs


@pytest.fixture()
def mock_wes(request):
    mock_wes = mock.Mock(name='mock WES')
    with mock.patch('synorchestrator.wes.wrapper.WES', 
                    autospec=True, spec_set=True):
        yield mock_wes


@pytest.fixture()
def mock_submission(request):
    mock_submission = {
        'mock_sub': {
            'status': '',
            'data': {'wf': '',
                     'jsonyaml': '',
                     'attachments': []},
            'wes_id': 'mock_wes',
            'run': {}
        }
    }
    yield mock_submission
