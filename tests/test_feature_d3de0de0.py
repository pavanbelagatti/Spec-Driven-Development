import pytest
from fastapi.testclient import TestClient
from workspace.app import app

client = TestClient(app)


def test_health_status_code():
    response = client.get('/health')
    assert response.status_code == 200


def test_health_response_body():
    response = client.get('/health')
    assert response.json() == {"status": "ok"}


def test_health_content_type():
    response = client.get('/health')
    assert response.headers['content-type'].startswith('application/json')
