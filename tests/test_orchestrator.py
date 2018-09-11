import mock
import pytest
import datetime as dt

from bravado.requests_client import RequestsClient
from bravado.client import SwaggerClient, ResourceDecorator
from bravado.testing.response_mocks import BravadoResponseMock

from wfinterop.wes.wrapper import WES
from wfinterop.orchestrator import run_job
from wfinterop.orchestrator import run_submission
from wfinterop.orchestrator import run_queue
from wfinterop.orchestrator import run_all
from wfinterop.orchestrator import monitor_queue
from wfinterop.orchestrator import monitor


def test_run_job(mock_queue_config, mock_submission, mock_wes, monkeypatch):
    monkeypatch.setattr('wfinterop.orchestrator.queue_config', 
                        lambda: mock_queue_config)
    monkeypatch.setattr('wfinterop.orchestrator.fetch_queue_workflow', 
                        lambda x: mock_queue_config[x])
    monkeypatch.setattr('wfinterop.testbed.create_submission', 
                        lambda **kwargs: None)
    monkeypatch.setattr('wfinterop.orchestrator.WES', 
                        lambda wes_id: mock_wes)
    monkeypatch.setattr('wfinterop.orchestrator.update_submission', 
                        lambda w,x,y,z: None)

    mock_request = {'workflow_url': None,
                    'workflow_params': mock_submission['mock_sub']['data'],
                    'attachment': None}
    mock_wes.run_workflow.return_value = {'run_id': 'mock_run'}
    mock_wes.get_run_status.return_value = {'run_id': 'mock_run', 
                                            'state': 'QUEUED'}

    test_run_log = run_job(queue_id='mock_queue_1',
                           wes_id='mock_wes',
                           wf_jsonyaml=mock_submission['mock_sub']['data'])

    mock_wes.run_workflow.assert_called_once_with(mock_request)
    assert 'start_time' in test_run_log


def test_run_submission(mock_submission, 
                        mock_wes, 
                        monkeypatch):
    monkeypatch.setattr('wfinterop.orchestrator.get_submission_bundle', 
                        lambda x,y: mock_submission['mock_sub'])
    monkeypatch.setattr('wfinterop.orchestrator.update_submission', 
                        lambda w,x,y,z: None)

    mock_run_log = {'run_id': 'mock_run',
                    'start_time': '',
                    'status': 'QUEUED'}
    monkeypatch.setattr('wfinterop.orchestrator.run_job', 
                        lambda **kwargs: mock_run_log)
    mock_request = mock_submission['mock_sub']['data']

    test_run_log = run_submission(queue_id='mock_queue',
                                   submission_id='mock_sub')

    assert 'start_time' in test_run_log


def test_run_queue(mock_queue_config, mock_submission, monkeypatch):
    monkeypatch.setattr('wfinterop.orchestrator.queue_config', 
                        lambda: mock_queue_config)
    monkeypatch.setattr('wfinterop.orchestrator.get_submissions', 
                        lambda x,status: ['mock_sub'])
    monkeypatch.setattr('wfinterop.orchestrator.get_submission_bundle', 
                        lambda x,y: mock_submission['mock_sub'])
    mock_run_log = {'run_id': '',
                    'start_time': '',
                    'type': '',
                    'status': 'QUEUED'}
    monkeypatch.setattr('wfinterop.orchestrator.run_submission', 
                        lambda x,y,z: mock_run_log)

    test_queue_log = run_queue(queue_id='mock_queue_1', 
                               wes_id='local')

    log_fields = ['wes_id',
                  'run_id',
                  'status',
                  'start_time']

    assert all([key in test_queue_log[sub] 
                for sub in test_queue_log.keys()
                for key in log_fields])


def test_run_all(mock_queue_config, monkeypatch):
    monkeypatch.setattr('wfinterop.orchestrator.queue_config', 
                        lambda: mock_queue_config)

    mock_orchestrator_log = {
        'mock_queue_1': {
            'mock_sub': {
                'queue_id': 'mock_queue',
                'job': '',
                'wes_id': 'local',
                'run_id': 'mock_run',
                'status': 'QUEUED',
                'start_time': ''
            }
        },
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
    monkeypatch.setattr('wfinterop.orchestrator.run_queue', 
                        lambda x: mock_orchestrator_log[x])

    test_orchestrator_log = run_all()
    assert test_orchestrator_log == mock_orchestrator_log


def test_monitor_queue(mock_submission, mock_queue_log, mock_wes, monkeypatch):
    monkeypatch.setattr('wfinterop.orchestrator.get_submissions', 
                        lambda **kwargs: ['mock_sub'])
    monkeypatch.setattr('wfinterop.orchestrator.get_submission_bundle', 
                        lambda x,y: mock_submission['mock_sub'])
    monkeypatch.setattr('wfinterop.orchestrator.WES', 
                        lambda wes_id: mock_wes)
    monkeypatch.setattr('wfinterop.orchestrator.convert_timedelta', 
                        lambda x: 0)
    monkeypatch.setattr('wfinterop.orchestrator.ctime2datetime', 
                        lambda x: dt.datetime.now())
    monkeypatch.setattr('wfinterop.orchestrator.update_submission', 
                        lambda w,x,y,z: None)
    
    mock_wes.get_run_status.return_value = {'run_id': 'mock_run', 
                                            'state': 'RUNNING'}

    mock_start_time = dt.datetime.now()

    test_queue_log = monitor_queue('mock_queue_1')
    assert test_queue_log == mock_queue_log




