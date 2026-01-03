import os
import pytest
import requests

from unittest.mock import Mock, patch
from src.service.camunda_service import CamundaService

@pytest.fixture
def camunda_service_client():
    camunda_service = CamundaService(
        base_url = os.getenv('ZEEBE_REST_ADDRESS'),
        token_audience = os.getenv('CAMUNDA_TOKEN_AUDIENCE'),
        client_id = os.getenv('CAMUNDA_CLIENT_ID'),
        client_secret = os.getenv('CAMUNDA_CLIENT_SECRET'),
        auth_url = os.getenv('CAMUNDA_OAUTH_URL')
    )

    return camunda_service

@pytest.fixture
def camunda_service_client_with_token():
    camunda_service = CamundaService(
        base_url = os.getenv('ZEEBE_REST_ADDRESS'),
        token_audience = os.getenv('CAMUNDA_TOKEN_AUDIENCE'),
        client_id = os.getenv('CAMUNDA_CLIENT_ID'),
        client_secret = os.getenv('CAMUNDA_CLIENT_SECRET'),
        auth_url = os.getenv('CAMUNDA_OAUTH_URL')
    )

    camunda_service.access_token = "test_token"

    return camunda_service

@pytest.fixture
def mock_headers():

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer test_token"
    }

    return headers


@patch("src.service.camunda_service.requests.post")
def test_get_token_success(mock_post, camunda_service_client):

    # Arrange the mock response
    mock_response = Mock()
    mock_response.ok = True
    mock_response.json.return_value = { "access_token": "test_token"}
    mock_post.return_value = mock_response
    
    camunda_service_client.get_token()

    payload = {
        "grant_type": "client_credentials",
        "audience": camunda_service_client.token_audience,
        "client_id": camunda_service_client.client_id,
        "client_secret": camunda_service_client.client_secret
    }

    mock_post.assert_called_once_with(
        url=camunda_service_client.auth_url,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data=payload
    )

    assert camunda_service_client.access_token == "test_token"


@patch("src.service.camunda_service.logger")
@patch("src.service.camunda_service.requests.post")
def test_get_token_response_exception(mock_post, mock_logger, camunda_service_client):

    mock_response = Mock()
    mock_response.ok = False
    mock_post.return_value = mock_response

    camunda_service_client.get_token()

    mock_logger.error.assert_called_once()
    assert "Failed to authenticate. Status Code:" in mock_logger.error.call_args[0][0]


@patch("src.service.camunda_service.logger")
@patch("src.service.camunda_service.requests.post")
def test_get_token_request_exception(mock_post, mock_logger, camunda_service_client):
   
    mock_post.side_effect = requests.exceptions.RequestException()

    camunda_service_client.get_token()

    mock_logger.error.assert_called_once()
    assert "Failed to connect" in mock_logger.error.call_args[0][0]


@patch("src.service.camunda_service.requests.get")
def test_get_cluster_topology(mock_get, camunda_service_client_with_token, mock_headers):

    request_url = f"{camunda_service_client_with_token.base_url}/v2/topology"

    mock_response = Mock()
    mock_response.ok = True
    mock_response.return_value = True
    mock_get.return_value = mock_response

    result = camunda_service_client_with_token.get_cluster_topology()

    assert result == True
    mock_get.assert_called_once_with(
        url=request_url,
        headers=mock_headers
    )


@patch("src.service.camunda_service.logger")
@patch("src.service.camunda_service.requests.get")
def test_get_cluster_topology_response_exception(mock_get, mock_logger, camunda_service_client_with_token):

    mock_response = Mock()
    mock_response.ok = False
    mock_get.return_value = mock_response

    camunda_service_client_with_token.get_cluster_topology()

    mock_logger.error.assert_called_once()
    assert "Failed to get cluster topology'. Status Code:" in mock_logger.error.call_args[0][0]


@patch("src.service.camunda_service.logger")
@patch("src.service.camunda_service.requests.get")
def test_get_cluster_topology_request(mock_get, mock_logger, camunda_service_client_with_token):

    mock_get.side_effect = requests.exceptions.RequestException

    camunda_service_client_with_token.get_cluster_topology()

    mock_logger.error.assert_called_once()
    assert "Failed to connect" in mock_logger.error.call_args[0][0]