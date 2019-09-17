import logging
import os
import pytest
import mock
import yaml
import json

from ga4ghtest.converters.trs2wes import fetch_queue_workflow
from ga4ghtest.converters.trs2wes import store_verification
from ga4ghtest.converters.trs2wes import get_version
from ga4ghtest.converters.trs2wes import get_wf_info
from ga4ghtest.converters.trs2wes import get_wdl_inputs
from ga4ghtest.converters.trs2wes import modify_jsonyaml_paths
from ga4ghtest.converters.trs2wes import get_wf_descriptor
from ga4ghtest.converters.trs2wes import get_wf_params
from ga4ghtest.converters.trs2wes import get_wf_attachments
from ga4ghtest.converters.trs2wes import expand_globs
from ga4ghtest.converters.trs2wes import build_wes_request


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def test_fetch_queue_workflow(mock_orchestratorqueues,
                              mock_queue_config,
                              mock_trs,
                              monkeypatch):
    monkeypatch.setattr('ga4ghtest.core.config.queues_path',
                        str(mock_orchestratorqueues))
    monkeypatch.setattr('ga4ghtest.converters.trs2wes.queue_config',
                        lambda: mock_queue_config)
    monkeypatch.setattr('ga4ghtest.converters.trs2wes.TRS',
                        lambda trs_id: mock_trs)

    mock_trs.get_workflow_descriptor.return_value = {'url': 'mock_wf_url'}
    mock_trs.get_workflow_files.return_value = [{'file_type': 'SECONDARY_DESCRIPTOR',
                                                 'path': 'mock_path'}]
    mock_trs.get_workflow_descriptor_relative.return_value = {'url': 'mock_file_url'}

    fetch_queue_workflow('mock_queue_1')

    mock_config = {'workflow_id': 'mock_wf',
                   'version_id': 'develop',
                   'workflow_type': 'CWL',
                   'trs_id': 'mock_trs',
                   'workflow_url': 'mock_wf_url',
                   'workflow_attachments': ['mock_file_url'],
                   'wes_default': 'local',
                   'wes_opts': ['local'],
                   'target_queue': None}

    with open(str(mock_orchestratorqueues), 'r') as f:
        test_config = yaml.load(f)

    assert(test_config['mock_queue_1'] == mock_config)


def test_store_verification(mock_orchestratorqueues,
                            mock_queue_config,
                            monkeypatch):
    # GIVEN an orchestrator config file exists
    monkeypatch.setattr('ga4ghtest.core.config.queues_path',
                        str(mock_orchestratorqueues))
    monkeypatch.setattr('ga4ghtest.core.config.queue_config',
                        lambda: mock_queue_config)
    # WHEN an evaluation queue is added to the configuration of the
    # workflow orchestrator app
    store_verification(
        queue_id='mock_queue_1',
        wes_id='mock_wes'
    )

    mock_config = {'trs_id': 'mock_trs',
                   'workflow_id': 'mock_wf',
                   'version_id': 'develop',
                   'workflow_type': 'CWL',
                   'workflow_url': None,
                   'workflow_attachments': None,
                   'wes_default': 'local',
                   'wes_opts': ['local'],
                   'target_queue': None,
                   'wes_verified': ['mock_wes']}

    # THEN the evaluation queue config should be stored in the config file
    with open(str(mock_orchestratorqueues), 'r') as f:
        test_config = yaml.load(f)

    assert(test_config['mock_queue_1'] == mock_config)


def test_get_version_cwl(cwl_descriptor):
    test_version = get_version(extension='cwl',
                               workflow_file=cwl_descriptor)
    assert test_version == 'v1.0'


def test_get_version_wdl(wdl_descriptor):
    test_version = get_version(extension='wdl',
                               workflow_file=wdl_descriptor)
    assert test_version == 'draft-2'


def test_get_wf_info_cwl(cwl_descriptor):
    test_info = get_wf_info(workflow_path=cwl_descriptor)
    assert test_info == ('v1.0', 'CWL')


def test_get_wf_info_wdl(wdl_descriptor):
    test_info = get_wf_info(workflow_path=wdl_descriptor)
    assert test_info == ('draft-2', 'WDL')


def test_get_wdl_inputs(wdl_wf_attachment):
    test_inputs = get_wdl_inputs(wdl_wf_attachment['workflow_attachment'][1])
    assert test_inputs == {'File': ['ga4ghMd5.inputFile']}


def test_modify_jsonyaml_paths_cwl(cwl_jsonyaml, cwl_modified_params):
    test_params = modify_jsonyaml_paths(cwl_jsonyaml)
    assert test_params == cwl_modified_params(cwl_jsonyaml)


def test_modify_jsonyaml_paths_wdl(wdl_jsonyaml, wdl_modified_params):
    test_params = modify_jsonyaml_paths(wdl_jsonyaml,
                                        path_keys=['ga4ghMd5.inputFile'])
    assert test_params == wdl_modified_params(wdl_jsonyaml)


def test_get_wf_descriptor_cwl(cwl_descriptor):
    test_descriptor = get_wf_descriptor(cwl_descriptor)
    assert test_descriptor == [('workflow_url', cwl_descriptor)]


def test_get_wf_descriptor_wdl(wdl_descriptor):
    test_descriptor = get_wf_descriptor(wdl_descriptor)
    assert test_descriptor == [('workflow_url', wdl_descriptor)]


def test_get_wf_descriptor_cwl_attach(cwl_descriptor, cwl_wf_attachment):
    test_parts = get_wf_descriptor(cwl_descriptor, attach_descriptor=True)
    test_parts_dict = dict(test_parts)
    assert test_parts_dict['workflow_url'] == cwl_wf_attachment['workflow_url']
    assert test_parts_dict['workflow_attachment'][0] == cwl_wf_attachment['workflow_attachment'][0]
    assert test_parts_dict['workflow_attachment'][1].read() == cwl_wf_attachment['workflow_attachment'][1]


def test_get_wf_descriptor_wdl_attach(wdl_descriptor, wdl_wf_attachment):
    test_parts = get_wf_descriptor(wdl_descriptor, attach_descriptor=True)
    test_parts_dict = dict(test_parts)
    assert test_parts_dict['workflow_url'] == wdl_wf_attachment['workflow_url']
    assert test_parts_dict['workflow_attachment'][0] == wdl_wf_attachment['workflow_attachment'][0]
    assert test_parts_dict['workflow_attachment'][1].read() == wdl_wf_attachment['workflow_attachment'][1]


def test_get_wf_params_cwl(cwl_descriptor, cwl_jsonyaml, cwl_params):
    test_parts = get_wf_params(cwl_descriptor, 'CWL', cwl_jsonyaml)
    test_parts_dict = dict(test_parts)
    assert test_parts_dict['workflow_params'] == cwl_params


def test_get_wf_params_wdl(wdl_descriptor, wdl_jsonyaml, wdl_params):
    test_parts = get_wf_params(wdl_descriptor, 'WDL', wdl_jsonyaml)
    test_parts_dict = dict(test_parts)
    assert test_parts_dict['workflow_params'] == wdl_params


def test_get_wf_params_wdl_fix(wdl_descriptor, wdl_jsonyaml, wdl_modified_params):
    test_parts = get_wf_params(wdl_descriptor, 'WDL', wdl_jsonyaml, fix_paths=True)
    test_parts_dict = dict(test_parts)
    assert test_parts_dict['workflow_params'] == wdl_modified_params(wdl_jsonyaml)


def test_get_wf_attachments(cwl_descriptor, cwl_attachments, cwl_import_attachment):
    test_parts = get_wf_attachments(cwl_descriptor, cwl_attachments)
    test_parts_dict = dict(test_parts)
    assert test_parts_dict['workflow_attachment'][0] == cwl_import_attachment[0]
    assert test_parts_dict['workflow_attachment'][1].read() == cwl_import_attachment[1]


def test_expand_globs(cwl_descriptor):
    test_set = expand_globs([cwl_descriptor])
    if list(test_set)[0].startswith('http'):
        assert test_set == set([cwl_descriptor])
    else:
        assert test_set == set(['file://{}'.format(os.path.abspath(cwl_descriptor))])

def test_build_wes_request(cwl_descriptor,
                           cwl_jsonyaml,
                           cwl_attachments,
                           monkeypatch):
    monkeypatch.setattr('ga4ghtest.converters.trs2wes.get_wf_info', 
                        lambda x: ('CWL', 'v1.0'))
    monkeypatch.setattr('ga4ghtest.converters.trs2wes.get_wf_descriptor', 
                        lambda **kwargs: [])
    monkeypatch.setattr('ga4ghtest.converters.trs2wes.get_wf_params', 
                        lambda **kwargs: [])
    monkeypatch.setattr('ga4ghtest.converters.trs2wes.get_wf_attachments', 
                        lambda **kwargs: [])
    test_parts = build_wes_request(cwl_descriptor,
                                   cwl_jsonyaml,
                                   cwl_attachments)
    assert test_parts == []