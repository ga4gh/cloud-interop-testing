import mock
import pytest

from bravado.requests_client import RequestsClient
from bravado.client import SwaggerClient, ResourceDecorator
from bravado.testing.response_mocks import BravadoResponseMock

from ga4ghtest.services.trs.api import _get_trs_opts
from ga4ghtest.services.trs.api import _init_http_client
from ga4ghtest.services.trs.api import load_trs_client
from ga4ghtest.services.trs.controller import TRSService


def test__get_trs_opts(mock_trs_config, monkeypatch):
    monkeypatch.setattr('ga4ghtest.services.trs.api.trs_config',
                        lambda: mock_trs_config)
    test_trs_opts = _get_trs_opts('mock_trs')

    assert test_trs_opts == mock_trs_config['mock_trs']


def test__init_http_client(mock_trs_config):
    mock_opts = mock_trs_config['mock_trs']
    test_http_client = _init_http_client(opts=mock_opts)

    assert isinstance(test_http_client, RequestsClient)
    assert test_http_client.authenticator.host == mock_opts['host']
    assert test_http_client.authenticator.api_key == mock_opts['auth']


# def test_load_trs_client_from_spec(mock_trs_config, monkeypatch):
#     monkeypatch.setattr('ga4ghtest.services.trs.api._get_trs_opts',
#                         lambda x: mock_trs_config['mock_trs'])
#     mock_http_client = RequestsClient()
#     test_trs_client = load_trs_client(service_id='mock_trs',
#                                       http_client=mock_http_client)

#     assert isinstance(test_trs_client, ResourceDecorator)


class TestTRSService:
    """
    Tests methods for the :class:`TRS` class, which serve as the main
    Python interface for the GA4GH TRS API. The tests below are primarily
    checking whether each method is making calls to the correct path
    and correctly handling responses.
    """
    def test_init(self, mock_trs_client):
        trs_instance = TRSService(trs_id='mock_trs',
                           api_client=mock_trs_client)

        assert hasattr(trs_instance, 'api_client')
        assert hasattr(trs_instance.api_client, 'metadataGet')

    def test_get_metadata(self, mock_trs_client):
        mock_metadata = {
            'version': '1.0.0',
            'api_version': '1.0.0',
            'country': '',
            'friendly_name': 'mock_trs'
        }

        mock_response = BravadoResponseMock(result=mock_metadata)
        mock_trs_client.metadataGet.return_value.response = mock_response

        trs_instance = TRSService(trs_id='mock_trs', api_client=mock_trs_client)
        test_metadata = trs_instance.get_metadata()

        assert isinstance(test_metadata, dict)
        assert test_metadata == mock_metadata

    def test_get_workflow(self, mock_trs_client):
        mock_workflow = {
            'url': '',
            'id': 'mock_wf',
            'organization': '',
            'author': '',
            'toolclass': {},
            'versions': []
        }

        mock_response = BravadoResponseMock(result=mock_workflow)
        mock_trs_client.toolsIdGet.return_value.response = mock_response

        trs_instance = TRSService(trs_id='mock_trs', api_client=mock_trs_client)
        test_workflow = trs_instance.get_workflow('mock_wf')

        assert isinstance(test_workflow, dict)
        assert test_workflow == mock_workflow

    def test_get_workflow_versions(self, mock_trs_client):
        mock_workflow_versions = [
            {'url': '', 'id': ''},
            {'url': '', 'id': ''}
        ]

        mock_response = BravadoResponseMock(result=mock_workflow_versions)
        operator = mock_trs_client.toolsIdVersionsGet
        operator.return_value.response = mock_response

        trs_instance = TRSService(trs_id='mock_trs', api_client=mock_trs_client)
        test_workflow_versions = trs_instance.get_workflow_versions(
            id='mock_wf'
        )

        assert isinstance(test_workflow_versions, list)
        assert test_workflow_versions == mock_workflow_versions

    def test_get_workflow_descriptor(self, mock_trs_client):
        mock_workflow_descriptor = {'content': '', 'url': ''}

        mock_response = BravadoResponseMock(result=mock_workflow_descriptor)
        operator = mock_trs_client.toolsIdVersionsVersionIdTypeDescriptorGet
        operator.return_value.response = mock_response

        trs_instance = TRSService(trs_id='mock_trs', api_client=mock_trs_client)
        test_workflow_descriptor = trs_instance.get_workflow_descriptor(
            id='mock_wf',
            version_id='test',
            type='CWL'
        )

        assert isinstance(test_workflow_descriptor, dict)
        assert test_workflow_descriptor == mock_workflow_descriptor

    def test_get_workflow_descriptor_relative(self, mock_trs_client):
        mock_workflow_descriptor = {'content': '', 'url': ''}

        mock_response = BravadoResponseMock(result=mock_workflow_descriptor)
        operator = mock_trs_client.toolsIdVersionsVersionIdTypeDescriptorRelativePathGet
        operator.return_value.response = mock_response

        trs_instance = TRSService(trs_id='mock_trs', api_client=mock_trs_client)
        test_workflow_descriptor = trs_instance.get_workflow_descriptor_relative(
            id='mock_wf',
            version_id='test',
            type='CWL',
            relative_path=''
        )

        assert isinstance(test_workflow_descriptor, dict)
        assert test_workflow_descriptor == mock_workflow_descriptor

    def test_get_workflow_tests(self, mock_trs_client):
        mock_workflow_tests = [{'content': '', 'url': ''}]

        mock_response = BravadoResponseMock(result=mock_workflow_tests)
        operator = mock_trs_client.toolsIdVersionsVersionIdTypeTestsGet
        operator.return_value.response = mock_response

        trs_instance = TRSService(trs_id='mock_trs', api_client=mock_trs_client)
        test_workflow_tests = trs_instance.get_workflow_tests(
            id='mock_wf',
            version_id='test',
            type='CWL'
        )

        assert isinstance(test_workflow_tests, list)
        assert test_workflow_tests == mock_workflow_tests

    def test_get_workflow_files(self, mock_trs_client):
        mock_workflow_files = [{'path': '', 'file_type': ''}]

        mock_response = BravadoResponseMock(result=mock_workflow_files)
        operator = mock_trs_client.toolsIdVersionsVersionIdTypeFilesGet
        operator.return_value.response = mock_response

        trs_instance = TRSService(trs_id='mock_trs', api_client=mock_trs_client)
        test_workflow_files = trs_instance.get_workflow_files(
            id='mock_wf',
            version_id='test',
            type='CWL'
        )

        assert isinstance(test_workflow_files, list)
        assert test_workflow_files == mock_workflow_files