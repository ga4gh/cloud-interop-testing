import mock
import pytest
import datetime as dt

from bravado.requests_client import RequestsClient
from bravado.client import SwaggerClient, ResourceDecorator
from bravado.testing.response_mocks import BravadoResponseMock

from synorchestrator.wes.wrapper import WES
from synorchestrator.orchestrator import run_submission
from synorchestrator.orchestrator import run_queue
from synorchestrator.orchestrator import run_next_queued
from synorchestrator.orchestrator import check_queue
from synorchestrator.orchestrator import check_all
from synorchestrator.orchestrator import run_all
from synorchestrator.orchestrator import monitor_queue
from synorchestrator.orchestrator import monitor


@pytest.fixture()
def mock_queue_config():
    mock_queue_config = {
        'mock_queue': {
            'submission_type': '',
            'trs_id': 'mock_trs',
            'version_id': '',
            'workflow_id': 'mock_wf',
            'workflow_type': ''
        }
    }
    yield mock_queue_config


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


@pytest.fixture()
def mock_trs(request):
    mock_trs = mock.Mock(name='mock TRS')
    with mock.patch('synorchestrator.trs.client.TRSClient', 
                    autospec=True, spec_set=True):
        yield mock_trs


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
    mock_wes.run_workflow.return_value = {'run_id': 'mock_run'}
    mock_wes.get_run_status.return_value = {'run_id': 'mock_run', 
                                            'state': 'QUEUED'}

    test_run_data = run_submission(queue_id='mock_queue',
                                   submission_id='mock_sub')

    mock_wes.run_workflow.assert_called_once_with(mock_request['wf'],
                                                  mock_request['jsonyaml'],
                                                  mock_request['attachments'])
    assert 'start_time' in test_run_data


def test_run_queue(mock_queue_config, monkeypatch):
    monkeypatch.setattr('synorchestrator.orchestrator.queue_config', 
                        lambda: mock_queue_config)
    monkeypatch.setattr('synorchestrator.orchestrator.get_submissions', 
                        lambda x,status: ['mock_sub'])
    mock_run_data = {'run_id': '',
                     'start_time': '',
                     'type': '',
                     'status': 'QUEUED'}
    monkeypatch.setattr('synorchestrator.orchestrator.run_submission', 
                        lambda x,y,z: mock_run_data)

    test_submission_log = run_queue(queue_id='mock_queue', wes_id='mock_wes')

    log_fields = ['queue_id',
                  'job',
                  'wes_id',
                  'run_id',
                  'status',
                  'start_time']

    assert all([key in test_submission_log['mock_wf'][sub] 
                for sub in test_submission_log['mock_wf'].keys()
                for key in log_fields])


def test_run_next_queued(monkeypatch):
    monkeypatch.setattr('synorchestrator.orchestrator.get_submissions', 
                        lambda x,status: ['mock_sub'])
    mock_run_data = {'run_id': '',
                     'start_time': '',
                     'status': 'QUEUED',
                     'type': ''}
    monkeypatch.setattr('synorchestrator.orchestrator.run_submission', 
                        lambda x,y: mock_run_data)

    test_run_data = run_next_queued(queue_id='mock_queue')

    assert test_run_data == mock_run_data


def test_check_queue(mock_queue_config, 
                     mock_trs_config, 
                     mock_trs, 
                     monkeypatch):
    monkeypatch.setattr('synorchestrator.orchestrator.queue_config', 
                        lambda: mock_queue_config)
    monkeypatch.setattr('synorchestrator.orchestrator.trs_config', 
                        lambda: mock_trs_config)
    monkeypatch.setattr('synorchestrator.orchestrator.TRSClient', 
                        lambda host,auth,proto: mock_trs)
    monkeypatch.setattr('synorchestrator.orchestrator.fetch_checker', 
                        lambda trs,workflow_id: ({}, {}))
    monkeypatch.setattr('synorchestrator.orchestrator.build_checker_request', 
                        lambda x,y: {})
    monkeypatch.setattr('synorchestrator.orchestrator.create_submission', 
                        lambda w,x,y,type: 'mock_sub')
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
    monkeypatch.setattr('synorchestrator.orchestrator.run_queue', 
                        lambda x: mock_submission_log)

    test_submission_log = check_queue(queue_id='mock_queue', wes_id='mock_wes')

    assert test_submission_log == mock_submission_log


def test_check_all(mock_queue_config, monkeypatch):
    monkeypatch.setattr('synorchestrator.orchestrator.queue_config', 
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
    monkeypatch.setattr('synorchestrator.orchestrator.check_queue', 
                        lambda x,y: mock_submission_logs[y])

    mock_queue_wes_map = {
        'mock_queue': ['mock_wes_1', 'mock_wes_2']
    }
    test_submission_logs = check_all(mock_queue_wes_map)
    assert all([log in mock_submission_logs.values() 
                for log in test_submission_logs])


def test_run_all(mock_queue_config, monkeypatch):
    monkeypatch.setattr('synorchestrator.orchestrator.queue_config', 
                        lambda: mock_queue_config)

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
    monkeypatch.setattr('synorchestrator.orchestrator.run_queue', 
                        lambda x: mock_submission_log)

    test_submission_logs = run_all()
    assert test_submission_logs == [mock_submission_log]


def test_monitor_queue(mock_wes_config, mock_wes, monkeypatch):
    monkeypatch.setattr('synorchestrator.orchestrator.wes_config', 
                        lambda: mock_wes_config) 
    monkeypatch.setattr('synorchestrator.orchestrator.WES', 
                        lambda auth,auth_type,host,proto: mock_wes)
    monkeypatch.setattr('synorchestrator.orchestrator.convert_timedelta', 
                        lambda x: 0)
    monkeypatch.setattr('synorchestrator.orchestrator.ctime2datetime', 
                        lambda x: dt.datetime.now())
    
    mock_wes.get_run_status.return_value = {'run_id': 'mock_run', 
                                            'state': 'RUNNING'}

    mock_start_time = dt.datetime.now()
    mock_submission_log = {
        'mock_wf': {
            'mock_sub': {
                'queue_id': 'mock_queue',
                'job': '',
                'wes_id': 'mock_wes',
                'run_id': 'mock_run',
                'status': 'QUEUED',
                'start_time': mock_start_time
            }
        }
    }

    mock_queue_status = {
        'mock_wf': {
            'mock_sub': {
                'queue_id': 'mock_queue',
                'job': '',
                'wes_id': 'mock_wes',
                'run_id': 'mock_run',
                'status': 'RUNNING',
                'start_time': mock_start_time,
                'elapsed_time': 0
            }
        }
    }
    test_queue_status = monitor_queue('mock_wf', mock_submission_log)
    assert test_queue_status == mock_queue_status


def test_monitor(monkeypatch):
    mock_start_time = dt.datetime.now()
    mock_queue_status = {
        'mock_wf': {
            'mock_sub': {
                'queue_id': 'mock_queue',
                'job': '',
                'wes_id': 'mock_wes',
                'run_id': 'mock_run',
                'status': 'COMPLETE',
                'start_time': mock_start_time,
                'elapsed_time': 0
            }
        }
    }
    monkeypatch.setattr('synorchestrator.orchestrator.monitor_queue', 
                        lambda x,y: mock_queue_status)
     
    mock_submission_logs = [{
        'mock_wf': {
            'mock_sub': {
                'queue_id': 'mock_queue',
                'job': '',
                'wes_id': 'mock_wes',
                'run_id': 'mock_run',
                'status': 'QUEUED',
                'start_time': mock_start_time
            }
        }
    }]

    test_statuses = monitor(mock_submission_logs)
    assert test_statuses == [mock_queue_status]



