import pytest
from fastapi.testclient import TestClient
from workspace.app import app

client = TestClient(app)

@pytest.fixture
def create_short_url():
    def _create(url="https://example.com", expires_in_seconds=3600, max_clicks=None):
        data = {"url": url, "expires_in_seconds": expires_in_seconds}
        if max_clicks is not None:
            data["max_clicks"] = max_clicks
        response = client.post("/shorten", json=data)
        assert response.status_code == 201
        return response.json()
    return _create


def test_stats_endpoint_initial_click_count(create_short_url):
    # Create a short URL
    result = create_short_url()
    code = result["code"]

    # Get stats immediately
    stats_resp = client.get(f"/api/stats/{code}")
    assert stats_resp.status_code == 200
    stats_data = stats_resp.json()
    assert stats_data["code"] == code
    assert stats_data["url"] == result["url"]
    assert stats_data["click_count"] == 0


def test_stats_endpoint_after_one_redirect(create_short_url):
    # Create a short URL
    result = create_short_url()
    code = result["code"]

    # Perform one redirect without following
    redirect_resp = client.get(f"/{code}", follow_redirects=False)
    assert redirect_resp.status_code == 307
    assert redirect_resp.headers["location"] == result["url"]

    # Check stats again
    stats_resp = client.get(f"/api/stats/{code}")
    assert stats_resp.status_code == 200
    stats_data = stats_resp.json()
    assert stats_data["code"] == code
    assert stats_data["url"] == result["url"]
    assert stats_data["click_count"] == 1


def test_stats_endpoint_unknown_code():
    resp = client.get("/api/stats/unknowncode")
    assert resp.status_code == 404


def test_stats_does_not_increment_click_count(create_short_url):
    result = create_short_url()
    code = result["code"]

    # Get stats multiple times
    for _ in range(3):
        resp = client.get(f"/api/stats/{code}")
        assert resp.status_code == 200
        assert resp.json()["click_count"] == 0

    # Redirect once
    redirect_resp = client.get(f"/{code}", follow_redirects=False)
    assert redirect_resp.status_code == 307

    # Stats should now show 1
    stats_resp = client.get(f"/api/stats/{code}")
    assert stats_resp.json()["click_count"] == 1


def test_stats_for_expired_url(create_short_url):
    # Create URL with 1 second expiration
    result = create_short_url(expires_in_seconds=1)
    code = result["code"]

    # Wait for expiration
    import time
    time.sleep(1.1)

    # Redirect returns 410
    redirect_resp = client.get(f"/{code}", follow_redirects=False)
    assert redirect_resp.status_code == 410

    # Stats still return 0 click_count (no successful redirect)
    stats_resp = client.get(f"/api/stats/{code}")
    assert stats_resp.status_code == 200
    assert stats_resp.json()["click_count"] == 0


def test_stats_for_click_limit_reached(create_short_url):
    # Create URL with max_clicks=1
    result = create_short_url(max_clicks=1)
    code = result["code"]

    # First redirect succeeds
    resp1 = client.get(f"/{code}", follow_redirects=False)
    assert resp1.status_code == 307

    # Second redirect returns 410
    resp2 = client.get(f"/{code}", follow_redirects=False)
    assert resp2.status_code == 410

    # Stats show click_count=1
    stats_resp = client.get(f"/api/stats/{code}")
    assert stats_resp.status_code == 200
    assert stats_resp.json()["click_count"] == 1
