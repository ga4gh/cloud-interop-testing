import mock
import pytest

from bravado.requests_client import RequestsClient
from bravado.client import SwaggerClient, ResourceDecorator
from bravado.testing.response_mocks import BravadoResponseMock

from synorchestrator.wes.wrapper import WES
from synorchestrator.orchestrator import run_submission


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

@pytest.fixture()
def mock_wes(request):
    mock_wes = mock.Mock(name='mock WES')
    with mock.patch('synorchestrator.wes.wrapper.WES', 
                    autospec=True, spec_set=True):
        yield mock_wes


def test_run_submission(mock_submission, 
                        mock_wes, 
                        mock_wes_config, 
                        monkeypatch):
    monkeypatch.setattr('synorchestrator.orchestrator.get_submission_bundle', 
                        lambda x,y: mock_submission['mock_sub'])
    monkeypatch.setattr('synorchestrator.orchestrator.wes_config', 
                        lambda: mock_wes_config)
    monkeypatch.setattr('synorchestrator.orchestrator.WES', 
                        lambda x: mock_wes)
    monkeypatch.setattr('synorchestrator.orchestrator.update_submission', 
                        lambda w,x,y,z: None)

    mock_request = mock_submission['mock_sub']['data']
    mock_wes.run_workflow.return_value = {}

    test_run_data = run_submission(wes_id='mock_wes',
                                   submission_id='mock_sub')

    mock_wes.run_workflow.assert_called_once_with(mock_request['wf'],
                                                  mock_request['jsonyaml'],
                                                  mock_request['attachments'])
    assert 'start_time' in test_run_data
