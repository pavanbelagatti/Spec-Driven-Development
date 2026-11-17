import pytest
from fastapi.testclient import TestClient
from workspace.app import app

client = TestClient(app)

def test_api_welcome_status_and_content():
    response = client.get('/api/welcome')
    assert response.status_code == 200
    assert response.headers['content-type'].startswith('application/json')
    assert response.json() == {"message": "Welcome to LinkForge"}


def test_api_welcome_not_conflicted_with_code_route():
    # Create a short URL to get a valid code
    create_resp = client.post('/shorten', json={"url": "https://example.com"})
    assert create_resp.status_code == 201
    code = create_resp.json()['code']

    # GET /api/welcome should still return welcome message
    welcome_resp = client.get('/api/welcome')
    assert welcome_resp.status_code == 200
    assert welcome_resp.json() == {"message": "Welcome to LinkForge"}

    # GET /{code} should redirect
    redirect_resp = client.get(f'/{code}', follow_redirects=False)
    assert redirect_resp.status_code == 307
    assert redirect_resp.headers['location'] == "https://example.com"
