import os
import pytest
import requests
from pathlib import Path

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

    # Arrange
    mock_response = Mock()
    mock_response.ok = True
    mock_response.json.return_value = { "access_token": "test_token"}
    mock_post.return_value = mock_response
    
    # Act
    camunda_service_client.get_token()

    payload = {
        "grant_type": "client_credentials",
        "audience": camunda_service_client.token_audience,
        "client_id": camunda_service_client.client_id,
        "client_secret": camunda_service_client.client_secret
    }

    # Assert
    mock_post.assert_called_once_with(
        url=camunda_service_client.auth_url,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data=payload
    )

    assert camunda_service_client.access_token == "test_token"


@patch("src.service.camunda_service.logger")
@patch("src.service.camunda_service.requests.post")
def test_get_token_response_exception(mock_post, mock_logger, camunda_service_client):

    # Arrange
    mock_response = Mock()
    mock_response.ok = False
    mock_post.return_value = mock_response

    # Act
    camunda_service_client.get_token()

    # Assert
    mock_logger.error.assert_called_once()
    assert "Failed to authenticate. Status Code:" in mock_logger.error.call_args[0][0]


@patch("src.service.camunda_service.logger")
@patch("src.service.camunda_service.requests.post")
def test_get_token_request_exception(mock_post, mock_logger, camunda_service_client):
   
    # Arrange
    mock_post.side_effect = requests.exceptions.RequestException()

    # Act
    camunda_service_client.get_token()

    # Assert
    mock_logger.error.assert_called_once()
    assert "Failed to connect" in mock_logger.error.call_args[0][0]


@patch("src.service.camunda_service.requests.get")
def test_get_cluster_topology_success(mock_get, camunda_service_client_with_token, mock_headers):

    # Arrange
    request_url = f"{camunda_service_client_with_token.base_url}/v2/topology"

    mock_response = Mock()
    mock_response.ok = True
    mock_response.return_value = True
    mock_get.return_value = mock_response

    # Act
    result = camunda_service_client_with_token.get_cluster_topology()

    # Assert
    assert result == True
    mock_get.assert_called_once_with(
        url=request_url,
        headers=mock_headers
    )


@patch("src.service.camunda_service.logger")
@patch("src.service.camunda_service.requests.get")
def test_get_cluster_topology_response_exception(mock_get, mock_logger, camunda_service_client_with_token):

    # Arrange
    mock_response = Mock()
    mock_response.ok = False
    mock_get.return_value = mock_response

    # Act
    result = camunda_service_client_with_token.get_cluster_topology()

    # Assert
    assert result is False
    mock_logger.error.assert_called_once()
    assert "Failed to get cluster topology'. Status Code:" in mock_logger.error.call_args[0][0]


@patch("src.service.camunda_service.logger")
@patch("src.service.camunda_service.requests.get")
def test_get_cluster_topology_request_exception(mock_get, mock_logger, camunda_service_client_with_token):

    # Arrange
    mock_get.side_effect = requests.exceptions.RequestException

    # Act
    result = camunda_service_client_with_token.get_cluster_topology()

    # Assert
    assert result is False
    mock_logger.error.assert_called_once()
    assert "Failed to connect" in mock_logger.error.call_args[0][0]


def get_deploy_resources() -> list[str]:
    """
    Helper method for the test_deploy_resources methods

    Returns:
        list[str]: List of paths of resources
    """

    resources_dir = "./src/assets"
    resource_paths = [resources_dir + "/" + file for file in os.listdir(resources_dir)]
    return resource_paths

@patch("src.service.camunda_service.requests.post")
def test_deploy_resources_success(mock_post, camunda_service_client_with_token):

    # Arrange
    request_url = f"{camunda_service_client_with_token.base_url}/v2/deployments"

    resource_paths = get_deploy_resources()

    mock_response = Mock()
    mock_response.ok = True
    mock_response.json.return_value = { "deploymentKey": "test_deployment_key" }
    mock_post.return_value = mock_response

    # Act
    result = camunda_service_client_with_token.deploy_resources(resource_paths=resource_paths)

    call_kwargs = mock_post.call_args[1]

    # Assert
    assert result == "test_deployment_key"
    mock_post.assert_called_once()
    assert call_kwargs["url"] == request_url
    assert call_kwargs["headers"]["Authorization"] == "Bearer test_token"
    assert "files" in call_kwargs
    assert len(call_kwargs["files"]) == len(resource_paths)


@patch("src.service.camunda_service.logger")
@patch("src.service.camunda_service.requests.post")
def test_deploy_resources_response_exception(mock_post, mock_logger, camunda_service_client_with_token):

    # Arrange
    resource_paths = get_deploy_resources()

    mock_response = Mock()
    mock_response.ok = False
    mock_post.return_value = mock_response

    # Act
    result = camunda_service_client_with_token.deploy_resources(resource_paths=resource_paths)

    # Assert
    assert result == ""
    assert "Failed to deploy resources" in mock_logger.error.call_args[0][0]