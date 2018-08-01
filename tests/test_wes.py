import mock
import pytest

from bravado.requests_client import RequestsClient
from bravado.client import SwaggerClient, ResourceDecorator
from bravado.testing.response_mocks import BravadoResponseMock

import synorchestrator.wes.client as wes_client
import synorchestrator.wes.wrapper as wes_wrapper


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


@pytest.fixture
def mock_api_client():
    mock_api_client = mock.Mock(name='mock SwaggerClient')
    with mock.patch.object(SwaggerClient, 'from_url', return_value=mock_api_client):
        yield mock_api_client


def test_init_http_client(mock_wes_config):
    mock_opts = mock_wes_config['mock_wes']
    test_http_client = wes_client.init_http_client(opts=mock_opts)

    assert isinstance(test_http_client, RequestsClient)
    assert test_http_client.authenticator.host == mock_opts['host']
    assert test_http_client.authenticator.api_key == mock_opts['auth']


def test_load_wes_client():
    mock_http_client = RequestsClient()
    test_wes_client = wes_client.load_wes_client(http_client=mock_http_client)

    assert isinstance(test_wes_client, ResourceDecorator)


def test_wes_get_service_info(mock_api_client):
    mock_service_info = {
        'workflow_type_versions': ['CWL', 'WDL']
    }

    mock_api_client.GetServiceInfo.return_value.response = BravadoResponseMock(
        result=mock_service_info
    )

    client = wes_wrapper.WES(api_client=mock_api_client)
    test_service_info = client.get_service_info()

    assert isinstance(test_service_info, dict) 
    assert test_service_info == mock_service_info

def test_wes_list_runs(mock_api_client):
    mock_runs = ['foo', 'bar']

    mock_api_client.ListRuns.return_value.response = BravadoResponseMock(result=mock_runs)

    client = wes_wrapper.WES(api_client=mock_api_client)
    test_runs = client.list_runs()

    assert isinstance(test_runs, list) 
    assert test_runs == mock_runs


def test_wes_run_workflow(mock_api_client):
    mock_run_id = {'run_id': 'foo'}

    mock_api_client.RunWorkflow.return_value.response = BravadoResponseMock(result=mock_run_id)
    client = wes_wrapper.WES(api_client=mock_api_client)
    test_run_id = client.run_workflow(request={})

    assert isinstance(test_run_id, dict) 
    assert test_run_id == mock_run_id


def test_wes_get_run(mock_api_client):
    mock_run_log = {'run_id': 'foo',
                    'request': {},
                    'state': '',
                    'run_log': {},
                    'task_logs': [],
                    'outputs': {}}

    mock_api_client.GetRunLog.return_value.response = BravadoResponseMock(result=mock_run_log)
    client = wes_wrapper.WES(api_client=mock_api_client)
    test_run_log = client.get_run(id='foo')

    assert isinstance(test_run_log, dict) 
    assert test_run_log == mock_run_log


def test_wes_get_run_status(mock_api_client):
    mock_run_status = {'run_id': 'foo',
                       'state': ''}

    mock_api_client.GetRunStatus.return_value.response = BravadoResponseMock(result=mock_run_status)
    client = wes_wrapper.WES(api_client=mock_api_client)
    test_run_status = client.get_run_status(id='foo')

    assert isinstance(test_run_status, dict) 
    assert test_run_status == mock_run_status
