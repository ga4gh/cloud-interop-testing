import mock
import pytest

from ga4ghtest.core.testbed import poll_services
from ga4ghtest.core.testbed import get_checker_id
from ga4ghtest.core.testbed import check_workflow
# from ga4ghtest.core.testbed import check_all


def test_poll_services(mock_queue_config,
                       mock_trs,
                       mock_wes,
                       monkeypatch):
    monkeypatch.setattr('ga4ghtest.core.testbed.queue_config',
                        lambda: mock_queue_config)
    monkeypatch.setattr('ga4ghtest.core.testbed.TRSService',
                        lambda trs_id: mock_trs)
    monkeypatch.setattr('ga4ghtest.core.testbed.WESService',
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
    monkeypatch.setattr('ga4ghtest.core.config.queues_path',
                        str(mock_orchestratorqueues))
    monkeypatch.setattr('ga4ghtest.core.testbed.testbed_log',
                        str(mock_testbedlog))
    monkeypatch.setattr('ga4ghtest.core.testbed.queue_config',
                        lambda: mock_queue_config)
    monkeypatch.setattr('ga4ghtest.core.testbed.TRSService',
                        lambda trs_id: mock_trs)
    monkeypatch.setattr('ga4ghtest.core.testbed.get_checker_id',
                        lambda x,y: 'mock_wf_checker')
    monkeypatch.setattr('ga4ghtest.core.testbed.add_queue',
                        lambda **kwargs: None)
    monkeypatch.setattr('ga4ghtest.core.testbed.create_submission',
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
    monkeypatch.setattr('ga4ghtest.core.testbed.run_submission',
                        lambda **kwargs: mock_run_log)

    test_testbed_status = check_workflow(queue_id='mock_queue_1',
                                         wes_id='local')

    assert test_testbed_status == mock_testbed_status


# def test_check_all(mock_queue_config, monkeypatch):
#     monkeypatch.setattr('ga4ghtest.core.testbed.queue_config',
#                         lambda: mock_queue_config)

#     mock_testbed_status = {
#         'mock_queue_1_checker': {
#             'mock_wes_1': {
#                 None: {
#                     'attach_descriptor': False,
#                     'attach_imports': False,
#                     'pack_descriptor': False,
#                     'resolve_params': False,
#                     'run_id': 'mock_run'
#                 }
#             }
#         }
#     }

#     monkeypatch.setattr('ga4ghtest.core.testbed.check_workflow',
#                         lambda **kwargs: mock_testbed_status)
#     monkeypatch.setattr('ga4ghtest.core.testbed.monitor_testbed',
#                         lambda: mock_testbed_status)

#     mock_workflow_wes_map = {
#         'mock_queue_1': ['mock_wes_1']
#     }
#     test_testbed_status = check_all(mock_workflow_wes_map)
#     assert test_testbed_status == mock_testbed_status