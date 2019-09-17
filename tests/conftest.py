import logging
import os
import pytest
import mock
import yaml
import json
import datetime as dt

from bravado.client import SwaggerClient, ResourceDecorator

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

mock_start_time = dt.datetime.now()


@pytest.fixture()
def mock_queue_config():
    mock_queue_config = {
        'mock_queue_1': {
            'trs_id': 'mock_trs',
            'workflow_id': 'mock_wf',
            'version_id': 'develop',
            'workflow_type': 'CWL',
            'workflow_url': None,
            'workflow_attachments': None,
            'wes_default': 'local',
            'wes_opts': ['local'],
            'target_queue': None
        },
        'mock_queue_1_checker': {
            'trs_id': 'mock_trs',
            'workflow_id': 'mock_wf_checker',
            'version_id': 'develop',
            'workflow_type': 'CWL',
            'workflow_url': None,
            'workflow_attachments': None,
            'wes_default': 'local',
            'wes_opts': ['local'],
            'target_queue': 'mock_queue_1'
        },
        'mock_queue_2': {
            'trs_id': 'mock_trs',
            'workflow_id': 'mock_wf',
            'version_id': 'prod',
            'workflow_type': 'CWL',
            'workflow_url': None,
            'workflow_attachments': None,
            'wes_default': 'local',
            'wes_opts': ['local'],
            'target_queue': None
        }
    }
    yield mock_queue_config


@pytest.fixture()
def mock_trs_config():
    mock_trs_config = {
        'mock_trs': {
            'auth': {'Authorization': 'Bearer auth_token'},
            'host': '0.0.0.0:8080',
            'proto': 'https'
        }
    }
    yield mock_trs_config


@pytest.fixture()
def mock_wes_config():
    mock_wes_config = {
        'mock_wes': {
            'auth': {'Authorization': 'Bearer auth_token'},
            'host': '0.0.0.0:8080',
            'proto': 'https'
        }
    }
    yield mock_wes_config


@pytest.fixture(scope='function')
def mock_orchestratorqueues(tmpdir,
                            mock_queue_config):
    # a mocked config file for a the orchestrator app
    logger.info("[setup] mock orchestrator queues file, create local file")

    mock_queues = mock_queue_config

    mock_queues_file = tmpdir.join('queues.yaml')
    logger.debug("writing queues file: {}".format(str(mock_queues_file)))
    mock_queues_file.write(yaml.dump(mock_queues, default_flow_style=False))

    yield mock_queues_file


@pytest.fixture(scope='function')
def mock_orchestratorconfig(tmpdir,
                            mock_trs_config,
                            mock_wes_config):
    # a mocked config file for a the orchestrator app
    logger.info("[setup] mock orchestrator config file, create local file")

    mock_config = {'toolregistries': mock_trs_config,
                   'workflowservices': mock_wes_config}
    mock_config_file = tmpdir.join('config.yaml')
    logger.debug("writing config file: {}".format(str(mock_config_file)))
    mock_config_file.write(yaml.dump(mock_config, default_flow_style=False))

    yield mock_config_file


@pytest.fixture(scope='function')
def mock_submissionqueue(tmpdir):
    logger.info("[setup] mock submission queue file, create local file")
    mock_queue = {}
    mock_queue_file = tmpdir.join('submission_queue.json')
    logger.debug("writing queue file: {}".format(str(mock_queue_file)))
    mock_queue_file.write(json.dumps(mock_queue, indent=4))

    yield mock_queue_file


@pytest.fixture(scope='function')
def mock_testbedlog(tmpdir):
    logger.info("[setup] mock testbed log file, create local file")
    mock_log = {}
    mock_log_file = tmpdir.join('testbed_log.json')
    logger.debug("writing log file: {}".format(str(mock_log_file)))
    mock_log_file.write(json.dumps(mock_log, indent=4))

    yield mock_log_file


@pytest.fixture()
def mock_client_lib(request):
    mock_wes_client = mock.Mock(name='mock WESClient')
    with mock.patch('wes_client.util.WESClient', 
                    autospec=True, spec_set=True):
        yield mock_wes_client


@pytest.fixture()
def mock_trs_client():
    mock_api_client = mock.Mock(name='mock SwaggerClient')
    with mock.patch.object(SwaggerClient, 'from_spec', 
                        return_value=mock_api_client):
        yield mock_api_client


@pytest.fixture(params=[None, 'workflow-service'])
def mock_wes_client(request):
    if request.param is None:
        mock_api_client = mock.Mock(name='mock SwaggerClient')
        with mock.patch.object(SwaggerClient, 'from_spec', 
                            return_value=mock_api_client):
            yield mock_api_client
    else:
        mock_api_client = mock.Mock(name='mock WESAdapter')
        with mock.patch('ga4ghtest.apis.wes.client.WESAdapter', 
                        autospec=True):
            yield mock_api_client


@pytest.fixture()
def mock_trs(request):
    mock_trs = mock.Mock(name='mock TRS')
    with mock.patch('ga4ghtest.apis.trs.wrapper.TRS', 
                    autospec=True, spec_set=True):
        yield mock_trs


@pytest.fixture()
def mock_wes(request):
    mock_wes = mock.Mock(name='mock WES')
    with mock.patch('ga4ghtest.apis.wes.wrapper.WES', 
                    autospec=True, spec_set=True):
        yield mock_wes


@pytest.fixture()
def mock_submission(request):
    mock_submission = {
        'mock_sub': {
            'status': '',
            'data': 'mock_json_url',
            'wes_id': 'mock_wes',
            'run_log': {'run_id': 'mock_run',
                        'status': '',
                        'start_time': mock_start_time}
        }
    }
    yield mock_submission


@pytest.fixture()
def mock_run_log():
    mock_run_log = {'run_id': 'mock_run',
                    'status': '',
                    'start_time': mock_start_time}
    yield mock_run_log


@pytest.fixture()
def mock_queue_log(request):
    mock_queue_log = {
        'mock_sub': {'run_id': 'mock_run',
                     'status': 'RUNNING',
                     'start_time': mock_start_time,
                     'elapsed_time': 0,
                     'wes_id': 'mock_wes'}
    }
    yield mock_queue_log

data_path = os.path.join(os.path.dirname(__file__), 'testdata')

@pytest.fixture(scope='function',
                params=[os.path.join(data_path, 'md5sum.cwl'),
                        'https://raw.githubusercontent.com/Sage-Bionetworks/workflow-interop/develop/tests/testdata/md5sum.cwl'],
                ids=['local', 'http'])
def cwl_descriptor(request):
    yield request.param


@pytest.fixture(scope='function',
                params=[os.path.join(data_path, 'md5sum.wdl'),
                        'https://raw.githubusercontent.com/Sage-Bionetworks/workflow-interop/develop/tests/testdata/md5sum.wdl'],
                ids=['local', 'http'])
def wdl_descriptor(request):
    yield request.param


@pytest.fixture()
def cwl_wf_attachment():
    with open(os.path.join(data_path, 'md5sum.cwl'), 'r') as f:
        cwl_contents = f.read()

    cwl_attach_parts = {
        'workflow_url': 'md5sum.cwl',
        'workflow_attachment': (
            'md5sum.cwl',
            cwl_contents
        )
    }
    yield cwl_attach_parts


@pytest.fixture()
def wdl_wf_attachment():
    with open(os.path.join(data_path, 'md5sum.wdl'), 'r') as f:
        wdl_contents = f.read()

    wdl_attach_parts = {
        'workflow_url': 'md5sum.wdl',
        'workflow_attachment': (
            'md5sum.wdl',
            wdl_contents
        )
    }
    yield wdl_attach_parts


@pytest.fixture(params=[os.path.join(data_path, 'md5sum.cwl.json'),
                        'https://raw.githubusercontent.com/Sage-Bionetworks/workflow-interop/develop/tests/testdata/md5sum.cwl.json'],
                ids=['local', 'http'])
def cwl_jsonyaml(request):
    yield request.param


@pytest.fixture()
def cwl_params():
    with open(os.path.join(data_path, 'md5sum.cwl.json'), 'r') as f:
        params = json.load(f)
    yield json.dumps(params)


@pytest.fixture()
def cwl_modified_params():

    def _loader(jsonyaml):
        jsonyaml_files = {
            os.path.join(data_path, 'md5sum.cwl.json'): os.path.join(data_path, 'md5sum.cwl.json'),
            'https://raw.githubusercontent.com/Sage-Bionetworks/workflow-interop/develop/tests/testdata/md5sum.cwl.json': os.path.join(data_path, 'md5sum.cwl.fixed.json')
        }
        with open(jsonyaml_files[jsonyaml], 'r') as f:
            params = json.load(f)
        if 'path' in params['input_file']:
            path = params['input_file'].pop('path')
            path = 'tests/testdata/{}'.format(path)
            params['input_file']['location'] = 'file://{}'.format(os.path.abspath(path))
        return json.dumps(params)

    return _loader


@pytest.fixture()
def wdl_modified_params():

    def _loader(jsonyaml):
        jsonyaml_files = {
            os.path.join(data_path, 'md5sum.wdl.json'): os.path.join(data_path, 'md5sum.wdl.json'),
            'https://raw.githubusercontent.com/Sage-Bionetworks/workflow-interop/develop/tests/testdata/md5sum.wdl.json': os.path.join(data_path, 'md5sum.wdl.fixed.json')
        }
        with open(jsonyaml_files[jsonyaml], 'r') as f:
            params = json.load(f)
        if not params['ga4ghMd5.inputFile'].startswith('http'):
            path = params['ga4ghMd5.inputFile']
            path = 'tests/testdata/{}'.format(path)
            params['ga4ghMd5.inputFile'] = 'file://{}'.format(os.path.abspath(path))
        return json.dumps(params)

    return _loader


@pytest.fixture(params=[os.path.join(data_path, 'md5sum.wdl.json'),
                        'https://raw.githubusercontent.com/Sage-Bionetworks/workflow-interop/develop/tests/testdata/md5sum.wdl.json'],
                ids=['local', 'http'])
def wdl_jsonyaml(request):
    yield request.param


@pytest.fixture()
def wdl_params():
    with open(os.path.join(data_path, 'md5sum.wdl.json'), 'r') as f:
        params = json.load(f)
    yield json.dumps(params)


@pytest.fixture(params=[os.path.join(data_path, 'dockstore-tool-md5sum.cwl'),
                        'https://raw.githubusercontent.com/Sage-Bionetworks/workflow-interop/develop/tests/testdata/dockstore-tool-md5sum.cwl'],
                ids=['local', 'http'])
def cwl_attachments(request):
    yield [request.param]


@pytest.fixture()
def cwl_import_attachment():
    with open(os.path.join(data_path, 'dockstore-tool-md5sum.cwl'), 'r') as f:
        attach_contents = f.read()
    yield ('dockstore-tool-md5sum.cwl', attach_contents)