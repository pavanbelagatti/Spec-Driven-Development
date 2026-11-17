import pytest
from fastapi.testclient import TestClient
from workspace.app import app

client = TestClient(app)


def test_count_endpoint_status():
    response = client.get('/api/count')
    assert response.status_code == 200


def test_count_endpoint_response_field_type():
    response = client.get('/api/count')
    assert response.status_code == 200
    data = response.json()
    assert 'total_urls' in data
    assert isinstance(data['total_urls'], int)


def test_count_increases_after_shorten():
    # Get initial count
    response_before = client.get('/api/count')
    assert response_before.status_code == 200
    count_before = response_before.json()['total_urls']

    # Create a new short URL
    shorten_payload = {
        "url": "https://example.com/test-count",
        "expires_in_seconds": 3600
    }
    response_shorten = client.post('/shorten', json=shorten_payload)
    assert response_shorten.status_code == 201

    # Get count after creation
    response_after = client.get('/api/count')
    assert response_after.status_code == 200
    count_after = response_after.json()['total_urls']

    assert count_after == count_before + 1
