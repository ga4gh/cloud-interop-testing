import mock
import pytest
import datetime as dt

from bravado.requests_client import RequestsClient
from bravado.client import SwaggerClient, ResourceDecorator
from bravado.testing.response_mocks import BravadoResponseMock

from synorchestrator.wes.wrapper import WES
from synorchestrator.orchestrator import run_job
from synorchestrator.orchestrator import run_submission
from synorchestrator.orchestrator import run_queue
from synorchestrator.orchestrator import run_next_queued
from synorchestrator.orchestrator import run_all
from synorchestrator.orchestrator import monitor_queue
from synorchestrator.orchestrator import monitor


def test_run_job(mock_queue_config, mock_submission, mock_wes, monkeypatch):
    monkeypatch.setattr('synorchestrator.orchestrator.queue_config', 
                        lambda: mock_queue_config)
    monkeypatch.setattr('synorchestrator.orchestrator.fetch_queue_workflow', 
                        lambda x: mock_queue_config[x])
    monkeypatch.setattr('synorchestrator.orchestrator.get_submission_bundle', 
                        lambda x,y: mock_submission['mock_sub'])
    monkeypatch.setattr('synorchestrator.orchestrator.WES', 
                        lambda wes_id: mock_wes)

    mock_request = {'workflow_url': None,
                    'workflow_params': mock_submission['mock_sub']['data'],
                    'attachment': None}
    mock_wes.run_workflow.return_value = {'run_id': 'mock_run'}
    mock_wes.get_run_status.return_value = {'run_id': 'mock_run', 
                                            'state': 'QUEUED'}

    test_run_data = run_job(queue_id='mock_queue_1',
                            wes_id='mock_wes',
                            wf_jsonyaml=mock_submission['mock_sub']['data'])

    mock_wes.run_workflow.assert_called_once_with(mock_request)
    assert 'start_time' in test_run_data


def test_run_submission(mock_submission, 
                        mock_wes, 
                        monkeypatch):
    monkeypatch.setattr('synorchestrator.orchestrator.get_submission_bundle', 
                        lambda x,y: mock_submission['mock_sub'])
    monkeypatch.setattr('synorchestrator.orchestrator.update_submission', 
                        lambda w,x,y,z: None)

    mock_run_data = {'run_id': 'mock_run',
                     'start_time': '',
                     'status': 'QUEUED'}
    monkeypatch.setattr('synorchestrator.orchestrator.run_job', 
                        lambda x,y,z: mock_run_data)
    mock_request = mock_submission['mock_sub']['data']

    test_run_data = run_submission(queue_id='mock_queue',
                                   submission_id='mock_sub')

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

    test_submission_log = run_queue(queue_id='mock_queue_1', 
                                    wes_id='local')

    log_fields = ['queue_id',
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


def test_run_all(mock_queue_config, monkeypatch):
    monkeypatch.setattr('synorchestrator.orchestrator.queue_config', 
                        lambda: mock_queue_config)
    queue_log_map = {'mock_queue_1': 1,
                     'mock_queue_2': 0}
    mock_submission_logs = [
        {
            'mock_queue_1': {
                'mock_sub': {
                    'queue_id': 'mock_queue',
                    'job': '',
                    'wes_id': 'local',
                    'run_id': 'mock_run',
                    'status': 'QUEUED',
                    'start_time': ''
                }
            }
        },
        {
            'mock_queue_2': {
                'mock_sub': {
                    'queue_id': 'mock_queue',
                    'job': '',
                    'wes_id': 'local',
                    'run_id': 'mock_run',
                    'status': 'QUEUED',
                    'start_time': ''
                }
            }
        }
    ]
    monkeypatch.setattr('synorchestrator.orchestrator.run_queue', 
                        lambda x: mock_submission_logs[queue_log_map[x]])

    test_submission_logs = run_all()
    assert test_submission_logs == mock_submission_logs


def test_monitor_queue(mock_wes, monkeypatch):
    # monkeypatch.setattr('synorchestrator.orchestrator.wes_config', 
    #                     lambda: mock_wes_config) 
    monkeypatch.setattr('synorchestrator.orchestrator.WES', 
                        lambda wes_id: mock_wes)
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



