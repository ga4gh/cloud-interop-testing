import logging
import mock
import pytest
import json
import datetime as dt

from wfinterop.queue import create_submission
from wfinterop.queue import get_submissions
from wfinterop.queue import get_submission_bundle
from wfinterop.queue import update_submission


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def test_create_submission(mock_submissionqueue, monkeypatch):
    monkeypatch.setattr('wfinterop.queue.submission_queue', 
                        str(mock_submissionqueue))

    test_sub_id = create_submission(queue_id='mock_queue_1',
                                    submission_data={})
    
    with open(str(mock_submissionqueue), 'r') as f:
        test_queue = json.load(f)

    mock_submission = {'data': {}, 'status': 'RECEIVED', 'wes_id': None}
    assert 'mock_queue_1' in test_queue
    assert test_sub_id in test_queue['mock_queue_1']
    assert test_queue['mock_queue_1'][test_sub_id] == mock_submission


def test_get_submissions(mock_submissionqueue, mock_submission, monkeypatch):
    monkeypatch.setattr('wfinterop.queue.submission_queue', 
                        str(mock_submissionqueue))
    mock_submission_data = mock_submission['mock_sub']
    mock_submission_data['status'] = 'RECEIVED'
    mock_submission_queue = {'mock_queue_1': 
                                {'mock_sub_1': mock_submission_data,
                                 'mock_sub_2': mock_submission_data}}
    monkeypatch.setattr('wfinterop.queue.get_json', 
                        lambda x: mock_submission_queue)
    
    test_submissions = get_submissions(queue_id='mock_queue_1',
                                       status=['RECEIVED'])
    
    test_submissions.sort()
    assert test_submissions == ['mock_sub_1', 'mock_sub_2']


def test_get_submission_bundle(mock_submissionqueue, 
                               mock_submission, 
                               monkeypatch):
    monkeypatch.setattr('wfinterop.queue.submission_queue', 
                        str(mock_submissionqueue))
    
    mock_queue = {'mock_queue_1': mock_submission}
    mock_submissionqueue.write(json.dumps(mock_queue, indent=4,
                               default=str))

    test_bundle = get_submission_bundle(queue_id='mock_queue_1',
                                        submission_id='mock_sub')
    mock_bundle = json.loads(json.dumps(mock_submission['mock_sub'], 
                                        default=str))
    assert test_bundle == mock_bundle


def test_update_submission(mock_submissionqueue, 
                           mock_submission, 
                           monkeypatch):
    monkeypatch.setattr('wfinterop.queue.submission_queue', 
                        str(mock_submissionqueue))

    mock_queue = {'mock_queue_1': mock_submission}
    mock_submissionqueue.write(json.dumps(mock_queue, indent=4,
                               default=str))

    update_submission('mock_queue_1', 'mock_sub', 'status', 'COMPLETE')

    with open(str(mock_submissionqueue), 'r') as f:
        test_queue = json.load(f)

    mock_submission['mock_sub']['status'] = 'COMPLETE'
    mock_bundle = json.loads(json.dumps(mock_submission['mock_sub'], 
                                        default=str))
    assert test_queue['mock_queue_1']['mock_sub'] == mock_bundle