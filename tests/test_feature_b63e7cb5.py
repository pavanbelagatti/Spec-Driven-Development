import pytest
from fastapi.testclient import TestClient
from workspace.app import app

client = TestClient(app)

def test_api_version_status_code():
    response = client.get('/api/version')
    assert response.status_code == 200

def test_api_version_response_body():
    response = client.get('/api/version')
    assert response.headers['content-type'].startswith('application/json')
    assert response.json() == {"version": "1.0.0"}
