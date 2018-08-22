import mock
import pytest

from synorchestrator.testbed import get_checker_id
from synorchestrator.testbed import check_workflow
from synorchestrator.testbed import check_all


@pytest.fixture()
def mock_testbed_config():
    mock_testbed_config = {
        'mock_wf': {
            'trs_id': 'mock_trs',
            'version_id': '',
            'type': '',
            'wes': []
        }
    }
    yield mock_testbed_config


@pytest.fixture()
def mock_queue_config():
    mock_queue_config = {
        'mock_queue': {
            'workflow_trs_id': 'mock_trs',
            'workflow_id': 'mock_wf',
            'workflow_version_id': '',
            'workflow_type': ''
        }
    }
    yield mock_queue_config


@pytest.fixture()
def mock_trs_config():
    mock_trs_config = {
        'mock_trs': {
            'auth': 'auth_token',
            'host': '0.0.0.0:8080',
            'proto': 'https'
        }
    }
    yield mock_trs_config


@pytest.fixture()
def mock_trs(request):
    mock_trs = mock.Mock(name='mock TRS')
    with mock.patch('synorchestrator.trs.wrapper.TRS', 
                    autospec=True, spec_set=True):
        yield mock_trs


def test_get_checker_id(mock_trs_config, mock_trs,  monkeypatch):
    monkeypatch.setattr('synorchestrator.testbed.TRS', 
                        lambda host,auth,proto: mock_trs)
    
    mock_checker_url = '/%23workflow%2Fmock_wf%2F_cwl_checker'
    mock_trs.get_workflow.return_value = {'checker_url': mock_checker_url}
    mock_checker_id = 'mock_wf/_cwl_checker'

    test_checker_id = get_checker_id(mock_trs, 'mock_wf')

    assert test_checker_id == mock_checker_id


def test_check_queue(mock_testbed_config,
                     mock_queue_config, 
                     mock_trs_config, 
                     mock_trs, 
                     monkeypatch):
    monkeypatch.setattr('synorchestrator.testbed.testbed_config', 
                        lambda: mock_testbed_config)
    monkeypatch.setattr('synorchestrator.testbed.queue_config', 
                        lambda: mock_queue_config)
    monkeypatch.setattr('synorchestrator.testbed.trs_config', 
                        lambda: mock_trs_config)
    monkeypatch.setattr('synorchestrator.testbed.TRS', 
                        lambda host,auth,proto: mock_trs)                        
    monkeypatch.setattr('synorchestrator.testbed.get_checker_id', 
                        lambda x,y: 'mock_wf_checker')
    monkeypatch.setattr('synorchestrator.testbed.create_queue', 
                        lambda workflow: 'mock_queue')
    monkeypatch.setattr('synorchestrator.testbed.create_submission', 
                        lambda queue_id,submission_data,wes_id,type: 'mock_sub')
    
    mock_trs.get_workflow_tests.return_value = [{'content': '', 'url': ''}]

    mock_submission_log = {
        'mock_wf': {
            'mock_sub': {
                'queue_id': 'mock_queue',
                'job': '',
                'wes_id': '',
                'run_id': 'mock_run',
                'status': 'QUEUED',
                'start_time': ''
            }
        }
    }
    monkeypatch.setattr('synorchestrator.testbed.run_queue', 
                        lambda x: mock_submission_log)

    test_submission_log = check_workflow(workflow_id='mock_wf', 
                                         wes_id='mock_wes')

    assert test_submission_log == mock_submission_log


def test_check_all(mock_testbed_config, monkeypatch):
    monkeypatch.setattr('synorchestrator.testbed.queue_config', 
                        lambda: mock_queue_config)

    mock_submission_logs = {
        'mock_wes_1': {
            'mock_wf': {
                'mock_sub': {
                    'queue_id': 'mock_queue',
                    'job': '',
                    'wes_id': 'mock_wes_1',
                    'run_id': 'mock_run',
                    'status': 'QUEUED',
                    'start_time': ''
                }
            }
        },
        'mock_wes_2': {
            'mock_wf': {
                'mock_sub': {
                    'queue_id': 'mock_queue',
                    'job': '',
                    'wes_id': 'mock_wes_2',
                    'run_id': 'mock_run',
                    'status': 'QUEUED',
                    'start_time': ''
                }
            }
        }
    }
    monkeypatch.setattr('synorchestrator.testbed.check_workflow', 
                        lambda x,y: mock_submission_logs[y])

    mock_workflow_wes_map = {
        'mock_wf': ['mock_wes_1', 'mock_wes_2']
    }
    test_submission_logs = check_all(mock_workflow_wes_map)
    assert all([log in mock_submission_logs.values() 
                for log in test_submission_logs])