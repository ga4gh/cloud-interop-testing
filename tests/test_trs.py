import mock
import pytest

from bravado.requests_client import RequestsClient
from bravado.client import SwaggerClient, ResourceDecorator
from bravado.testing.response_mocks import BravadoResponseMock

from synorchestrator.trs.client import _get_trs_opts
from synorchestrator.trs.client import _init_http_client
from synorchestrator.trs.client import load_trs_client
from synorchestrator.trs.wrapper import TRS


@pytest.fixture()
def mock_trs_config():
    mock_trs_config = {
        'mock_trs': {
            'auth': 'auth_token',
            'auth_type': 'token',
            'host': '0.0.0.0:8080',
            'proto': 'https'
        }
    }
    yield mock_trs_config


@pytest.fixture
def mock_api_client():
    mock_api_client = mock.Mock(name='mock SwaggerClient')
    with mock.patch.object(SwaggerClient, 'from_url', 
                           return_value=mock_api_client):
        yield mock_api_client


def test__get_trs_opts(mock_trs_config, monkeypatch):
    monkeypatch.setattr('synorchestrator.trs.client.trs_config', 
                        lambda: mock_trs_config)
    test_trs_opts = _get_trs_opts('mock_trs')

    assert test_trs_opts == mock_trs_config['mock_trs']


def test__init_http_client(mock_trs_config):
    mock_opts = mock_trs_config['mock_trs']
    test_http_client = _init_http_client(opts=mock_opts)

    assert isinstance(test_http_client, RequestsClient)
    assert test_http_client.authenticator.host == mock_opts['host']
    assert test_http_client.authenticator.api_key == mock_opts['auth']


def test_load_trs_client_from_spec():
    mock_http_client = RequestsClient()
    test_trs_client = load_trs_client(service_id='mock_trs',
                                      http_client=mock_http_client)

    assert isinstance(test_trs_client, ResourceDecorator)


@pytest.fixture()
def mock_api_client():
    mock_api_client = mock.Mock(name='mock SwaggerClient')
    with mock.patch.object(SwaggerClient, 'from_url', 
                        return_value=mock_api_client):
        yield mock_api_client


class TestTRS:
    """
    Tests methods for the :class:`TRS` class, which serve as the main
    Python interface for the GA4GH TRS API. The tests below are primarily
    checking whether each method is making calls to the correct path
    and correctly handling responses.
    """
    def test_init(self, mock_api_client):
        trs_instance = TRS(trs_id='mock_trs', 
                           api_client=mock_api_client)

        assert hasattr(trs_instance, 'api_client')
        assert hasattr(trs_instance.api_client, 'metadataGet')  
        
    def test_get_metadata(self, mock_api_client):
        mock_metadata = {
            'version': '1.0.0',
            'api_version': '1.0.0',
            'country': '',
            'friendly_name': 'mock_trs'
        }

        mock_response = BravadoResponseMock(result=mock_metadata)
        mock_api_client.metadataGet.return_value.response = mock_response

        trs_instance = TRS(trs_id='mock_trs', api_client=mock_api_client)
        test_metadata = trs_instance.get_metadata()

        assert isinstance(test_metadata, dict) 
        assert test_metadata == mock_metadata

    def test_get_workflow(self, mock_api_client):
        mock_workflow = {
            'url': '',
            'id': 'mock_wf',
            'organization': '',
            'author': '',
            'toolclass': {},
            'versions': []
        }

        mock_response = BravadoResponseMock(result=mock_workflow)
        mock_api_client.toolsIdGet.return_value.response = mock_response

        trs_instance = TRS(trs_id='mock_trs', api_client=mock_api_client)
        test_workflow = trs_instance.get_workflow('mock_wf')

        assert isinstance(test_workflow, dict) 
        assert test_workflow == mock_workflow  

    def test_get_workflow_versions(self, mock_api_client):
        mock_workflow_versions = [
            {'url': '', 'id': ''},
            {'url': '', 'id': ''}
        ]

        mock_response = BravadoResponseMock(result=mock_workflow_versions)
        operator = mock_api_client.toolsIdVersionsGet
        operator.return_value.response = mock_response

        trs_instance = TRS(trs_id='mock_trs', api_client=mock_api_client)
        test_workflow_versions = trs_instance.get_workflow_versions(
            id='mock_wf'
        )

        assert isinstance(test_workflow_versions, list) 
        assert test_workflow_versions == mock_workflow_versions
    
    def test_get_workflow_descriptor(self, mock_api_client):
        mock_workflow_descriptor = {'content': '', 'url': ''}

        mock_response = BravadoResponseMock(result=mock_workflow_descriptor)
        operator = mock_api_client.toolsIdVersionsVersionIdTypeDescriptorGet
        operator.return_value.response = mock_response

        trs_instance = TRS(trs_id='mock_trs', api_client=mock_api_client)
        test_workflow_descriptor = trs_instance.get_workflow_descriptor(
            id='mock_wf',
            version_id='test',
            type='CWL'
        )

        assert isinstance(test_workflow_descriptor, dict) 
        assert test_workflow_descriptor == mock_workflow_descriptor
    
    def test_get_workflow_descriptor_relative(self, mock_api_client):
        mock_workflow_descriptor = {'content': '', 'url': ''}

        mock_response = BravadoResponseMock(result=mock_workflow_descriptor)
        operator = mock_api_client.toolsIdVersionsVersionIdTypeDescriptorRelativePathGet
        operator.return_value.response = mock_response

        trs_instance = TRS(trs_id='mock_trs', api_client=mock_api_client)
        test_workflow_descriptor = trs_instance.get_workflow_descriptor_relative(
            id='mock_wf',
            version_id='test',
            type='CWL',
            relative_path=''
        )

        assert isinstance(test_workflow_descriptor, dict) 
        assert test_workflow_descriptor == mock_workflow_descriptor
    
    def test_get_workflow_tests(self, mock_api_client):
        mock_workflow_tests = [{'content': '', 'url': ''}]

        mock_response = BravadoResponseMock(result=mock_workflow_tests)
        operator = mock_api_client.toolsIdVersionsVersionIdTypeTestsGet
        operator.return_value.response = mock_response

        trs_instance = TRS(trs_id='mock_trs', api_client=mock_api_client)
        test_workflow_tests = trs_instance.get_workflow_tests(
            id='mock_wf',
            version_id='test',
            type='CWL'
        )

        assert isinstance(test_workflow_tests, list) 
        assert test_workflow_tests == mock_workflow_tests

    def test_get_workflow_files(self, mock_api_client):
        mock_workflow_files = [{'path': '', 'file_type': ''}]

        mock_response = BravadoResponseMock(result=mock_workflow_files)
        operator = mock_api_client.toolsIdVersionsVersionIdTypeFilesGet
        operator.return_value.response = mock_response

        trs_instance = TRS(trs_id='mock_trs', api_client=mock_api_client)
        test_workflow_files = trs_instance.get_workflow_files(
            id='mock_wf',
            version_id='test',
            type='CWL'
        )

        assert isinstance(test_workflow_files, list) 
        assert test_workflow_files == mock_workflow_files