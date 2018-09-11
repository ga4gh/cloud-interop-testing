import logging
import pytest
import mock
import yaml
import datetime as dt

from bravado.client import SwaggerClient, ResourceDecorator

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

mock_start_time = dt.datetime.now()


@pytest.fixture()
def mock_queue_config():
    mock_queue_config = {
        'mock_queue_1': {
            'trs_id': 'mock_trs',
            'workflow_id': 'mock_wf',
            'version_id': 'develop',
            'workflow_type': 'CWL',
            'workflow_url': None,
            'workflow_attachments': None,
            'wes_default': 'local',
            'wes_opts': ['local'],
            'target_queue': None
        },
        'mock_queue_2': {
            'trs_id': 'mock_trs',
            'workflow_id': 'mock_wf',
            'version_id': 'prod',
            'workflow_type': 'CWL',
            'workflow_url': None,
            'workflow_attachments': None,
            'wes_default': 'local',
            'wes_opts': ['local'],
            'target_queue': None
        }
    }
    yield mock_queue_config


@pytest.fixture()
def mock_trs_config():
    mock_trs_config = {
        'mock_trs': {
            'auth': {'Authorization': 'Bearer auth_token'},
            'host': '0.0.0.0:8080',
            'proto': 'https'
        }
    }
    yield mock_trs_config


@pytest.fixture()
def mock_wes_config():
    mock_wes_config = {
        'mock_wes': {
            'auth': {'Authorization': 'Bearer auth_token'},
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
        with mock.patch('wfinterop.wes.client.WESAdapter', 
                        autospec=True):
            yield mock_api_client


@pytest.fixture()
def mock_trs(request):
    mock_trs = mock.Mock(name='mock TRS')
    with mock.patch('wfinterop.trs.wrapper.TRS', 
                    autospec=True, spec_set=True):
        yield mock_trs


@pytest.fixture()
def mock_wes(request):
    mock_wes = mock.Mock(name='mock WES')
    with mock.patch('wfinterop.wes.wrapper.WES', 
                    autospec=True, spec_set=True):
        yield mock_wes


@pytest.fixture()
def mock_submission(request):
    mock_submission = {
        'mock_sub': {
            'status': '',
            'data': 'mock_json_url',
            'wes_id': 'mock_wes',
            'run_log': {'run_id': 'mock_run',
                        'status': '',
                        'start_time': mock_start_time}
        }
    }
    yield mock_submission


@pytest.fixture()
def mock_queue_log(request):
    mock_queue_log = {
        'mock_sub': {'run_id': 'mock_run',
                     'status': 'RUNNING',
                     'start_time': mock_start_time,
                     'elapsed_time': 0,
                     'wes_id': 'mock_wes'}
    }
    yield mock_queue_log