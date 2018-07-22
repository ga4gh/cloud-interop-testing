import mock
import pytest

from bravado.requests_client import RequestsClient
from bravado.client import SwaggerClient, ResourceDecorator
from bravado.testing.response_mocks import BravadoResponseMock

import synorchestrator.trs.client as trs_client
import synorchestrator.trs.wrapper as trs_wrapper

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


def test__get_trs_opts(mock_trs_config):

    test_trs_opts = trs_client._get_trs_opts('mock_trs', mock_trs_config)

    assert test_trs_opts == mock_trs_config['mock_trs']


def test__init_http_client(mock_trs_config):
    mock_opts = mock_trs_config['mock_trs']
    test_http_client = trs_client._init_http_client(opts=mock_opts)

    assert isinstance(test_http_client, RequestsClient)
    assert test_http_client.authenticator.host == mock_opts['host']
    assert test_http_client.authenticator.api_key == mock_opts['auth']


def test_load_trs_client():
    mock_http_client = RequestsClient()
    test_trs_client = trs_client.load_trs_client(http_client=mock_http_client)
    
    assert isinstance(test_trs_client, ResourceDecorator)


def test_trs_get_metadata(mock_api_client):
    mock_metadata = {
        'version': '1.0.0',
        'api_version': '1.0.0',
        'country': '',
        'friendly_name': 'mock_trs'
    }

    mock_api_client.metadataGet.return_value.response = BravadoResponseMock(
        result=mock_metadata
    )

    client = trs_wrapper.TRS(api_client=mock_api_client)
    test_metadata = client.get_metadata()

    assert isinstance(test_metadata, dict) 
    assert test_metadata == mock_metadata