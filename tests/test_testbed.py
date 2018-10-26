import mock
import pytest

from wfinterop.testbed import poll_services
from wfinterop.testbed import get_checker_id
from wfinterop.testbed import check_workflow
from wfinterop.testbed import check_all


def test_poll_services(mock_queue_config, 
                       mock_trs,
                       mock_wes,
                       monkeypatch):
    monkeypatch.setattr('wfinterop.testbed.queue_config', 
                        lambda: mock_queue_config)
    monkeypatch.setattr('wfinterop.testbed.TRS', 
                        lambda trs_id: mock_trs) 
    monkeypatch.setattr('wfinterop.testbed.WES', 
                        lambda wes_id: mock_wes)  

    test_service_status = poll_services()
    assert test_service_status == {'toolregistries': {'mock_trs': True},
                                   'workflowservices': {'local': True}}


def test_get_checker_id(mock_trs,  monkeypatch):
    mock_checker_url = '/%23workflow%2Fmock_wf%2F_cwl_checker'
    mock_trs.get_workflow.return_value = {'checker_url': mock_checker_url}
    mock_checker_id = 'mock_wf/_cwl_checker'

    test_checker_id = get_checker_id(mock_trs, 'mock_wf')

    assert test_checker_id == mock_checker_id


def test_check_workflow(mock_orchestratorqueues,
                        mock_testbedlog,
                        mock_queue_config, 
                        mock_trs, 
                        monkeypatch):
    monkeypatch.setattr('wfinterop.config.queues_path', 
                        str(mock_orchestratorqueues))
    monkeypatch.setattr('wfinterop.testbed.testbed_log', 
                        str(mock_testbedlog))
    monkeypatch.setattr('wfinterop.testbed.queue_config', 
                        lambda: mock_queue_config)
    monkeypatch.setattr('wfinterop.testbed.TRS', 
                        lambda trs_id: mock_trs)                        
    monkeypatch.setattr('wfinterop.testbed.get_checker_id', 
                        lambda x,y: 'mock_wf_checker')
    monkeypatch.setattr('wfinterop.testbed.add_queue', 
                        lambda **kwargs: None)
    monkeypatch.setattr('wfinterop.testbed.create_submission', 
                        lambda **kwargs: None)
    mock_trs.get_workflow_tests.return_value = [{'content': '', 'url': ''}]

    mock_run_log = {
        'queue_id': 'mock_queue',
        'job': '',
        'wes_id': '',
        'run_id': 'mock_run',
        'status': 'QUEUED',
        'start_time': ''
    }
    mock_testbed_status = {
        'mock_queue_1_checker': {
            'local': {
                None: {
                    'attach_descriptor': False,
                    'attach_imports': False,
                    'pack_descriptor': False,
                    'resolve_params': False,
                    'run_id': 'mock_run'
                }
            }
        }
    }
    monkeypatch.setattr('wfinterop.testbed.run_submission', 
                        lambda **kwargs: mock_run_log)

    test_testbed_status = check_workflow(queue_id='mock_queue_1', 
                                         wes_id='local')

    assert test_testbed_status == mock_testbed_status


def test_check_all(mock_queue_config, monkeypatch):
    monkeypatch.setattr('wfinterop.testbed.queue_config', 
                        lambda: mock_queue_config)

    mock_testbed_status = {
        'mock_queue_1_checker': {
            'mock_wes_1': {
                None: {
                    'attach_descriptor': False,
                    'attach_imports': False,
                    'pack_descriptor': False,
                    'resolve_params': False,
                    'run_id': 'mock_run'
                }
            }
        }
    }
    
    monkeypatch.setattr('wfinterop.testbed.check_workflow', 
                        lambda **kwargs: mock_testbed_status)
    monkeypatch.setattr('wfinterop.testbed.monitor_testbed', 
                        lambda: mock_testbed_status)

    mock_workflow_wes_map = {
        'mock_queue_1': ['mock_wes_1']
    }
    test_testbed_status = check_all(mock_workflow_wes_map)
    assert test_testbed_status == mock_testbed_status