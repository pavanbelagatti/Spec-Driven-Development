import pytest
from fastapi.testclient import TestClient
from workspace.app import app

client = TestClient(app)


def test_api_count_initial_and_after_creation():
    # Initially, count should be zero or reflect current store size
    response = client.get('/api/count')
    assert response.status_code == 200
    data = response.json()
    assert 'total_urls' in data
    initial_count = data['total_urls']
    assert isinstance(initial_count, int)
    assert initial_count >= 0

    # Create a new shortened URL
    payload = {
        "url": "https://example.com",
        "expires_in_seconds": 3600
    }
    create_resp = client.post('/shorten', json=payload)
    assert create_resp.status_code == 201
    create_data = create_resp.json()
    assert 'code' in create_data

    # Count should increase by 1
    response_after = client.get('/api/count')
    assert response_after.status_code == 200
    data_after = response_after.json()
    assert 'total_urls' in data_after
    assert data_after['total_urls'] == initial_count + 1


def test_api_count_multiple_creations():
    # Get initial count
    response = client.get('/api/count')
    initial_count = response.json()['total_urls']

    # Create multiple URLs
    urls = [
        "https://test1.com",
        "https://test2.com",
        "https://test3.com"
    ]
    for url in urls:
        resp = client.post('/shorten', json={"url": url})
        assert resp.status_code == 201

    # Count should increase by len(urls)
    response_after = client.get('/api/count')
    assert response_after.status_code == 200
    data_after = response_after.json()
    assert data_after['total_urls'] == initial_count + len(urls)


def test_api_count_response_format():
    response = client.get('/api/count')
    assert response.status_code == 200
    assert response.headers['content-type'].startswith('application/json')
    data = response.json()
    assert isinstance(data, dict)
    assert 'total_urls' in data
    assert isinstance(data['total_urls'], int)
