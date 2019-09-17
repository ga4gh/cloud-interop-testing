import mock
import pytest
import datetime as dt

from bravado.requests_client import RequestsClient
from bravado.client import SwaggerClient, ResourceDecorator
from bravado.testing.response_mocks import BravadoResponseMock

from ga4ghtest.apis.wes.wrapper import WES
from ga4ghtest.core.orchestrator import run_job
from ga4ghtest.core.orchestrator import run_submission
from ga4ghtest.core.orchestrator import run_queue
from ga4ghtest.core.orchestrator import monitor_queue
from ga4ghtest.core.orchestrator import monitor


def test_run_job(mock_queue_config,
                 mock_wes_config,
                 mock_submission, 
                 mock_wes, 
                 monkeypatch):
    monkeypatch.setattr('ga4ghtest.core.orchestrator.queue_config', 
                        lambda: mock_queue_config)
    monkeypatch.setattr('ga4ghtest.core.orchestrator.wes_config', 
                        lambda: mock_wes_config)
    monkeypatch.setattr('ga4ghtest.core.orchestrator.fetch_queue_workflow', 
                        lambda x: mock_queue_config[x])
    monkeypatch.setattr('ga4ghtest.core.orchestrator.create_submission', 
                        lambda **kwargs: None)
    monkeypatch.setattr('ga4ghtest.core.orchestrator.WES', 
                        lambda wes_id: mock_wes)
    monkeypatch.setattr('ga4ghtest.core.orchestrator.update_submission', 
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

    mock_wes.run_workflow.assert_called_once_with(mock_request, parts=None)
    assert 'start_time' in test_run_log


def test_run_submission(mock_submission, 
                        mock_run_log,
                        mock_wes, 
                        monkeypatch):
    monkeypatch.setattr('ga4ghtest.core.orchestrator.get_submission_bundle', 
                        lambda x,y: mock_submission['mock_sub'])
    monkeypatch.setattr('ga4ghtest.core.orchestrator.update_submission', 
                        lambda w,x,y,z: None)

    monkeypatch.setattr('ga4ghtest.core.orchestrator.run_job', 
                        lambda **kwargs: mock_run_log)

    test_run_log = run_submission(queue_id='mock_queue',
                                  submission_id='mock_sub')

    assert test_run_log == mock_run_log


def test_run_queue(mock_queue_config, 
                   mock_submission,
                   mock_queue_log,
                   monkeypatch):
    monkeypatch.setattr('ga4ghtest.core.orchestrator.queue_config', 
                        lambda: mock_queue_config)
    monkeypatch.setattr('ga4ghtest.core.orchestrator.get_submissions', 
                        lambda x,status: ['mock_sub'])
    monkeypatch.setattr('ga4ghtest.core.orchestrator.get_submission_bundle', 
                        lambda x,y: mock_submission['mock_sub'])

    mock_run_log = mock_submission['mock_sub']['run_log']
    monkeypatch.setattr('ga4ghtest.core.orchestrator.run_submission', 
                        lambda **kwargs: mock_run_log)

    test_queue_log = run_queue(queue_id='mock_queue_1', 
                               wes_id='local')

    mock_queue_log['mock_sub']['status'] = ''
    mock_queue_log['mock_sub'].pop('elapsed_time')

    assert test_queue_log == mock_queue_log


def test_monitor_queue(mock_submission, 
                       mock_queue_log, 
                       mock_wes, 
                       monkeypatch):
    monkeypatch.setattr('ga4ghtest.core.orchestrator.get_submissions', 
                        lambda **kwargs: ['mock_sub'])
    monkeypatch.setattr('ga4ghtest.core.orchestrator.get_submission_bundle', 
                        lambda x,y: mock_submission['mock_sub'])
    monkeypatch.setattr('ga4ghtest.core.orchestrator.WES', 
                        lambda wes_id: mock_wes)
    monkeypatch.setattr('ga4ghtest.core.orchestrator.convert_timedelta', 
                        lambda x: 0)
    monkeypatch.setattr('ga4ghtest.core.orchestrator.ctime2datetime', 
                        lambda x: dt.datetime.now())
    monkeypatch.setattr('ga4ghtest.core.orchestrator.update_submission', 
                        lambda w,x,y,z: None)

    mock_wes.get_run_status.return_value = {'run_id': 'mock_run', 
                                            'state': 'RUNNING'}

    mock_start_time = dt.datetime.now()

    test_queue_log = monitor_queue('mock_queue_1')
    assert test_queue_log == mock_queue_log




