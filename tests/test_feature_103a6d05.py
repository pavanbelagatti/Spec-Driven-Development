import pytest
from fastapi.testclient import TestClient
from workspace.app import app

client = TestClient(app)

# Helper function to create a shortened URL

def create_short_url(url, expires_in_seconds=None, max_clicks=None, alias=None):
    data = {"url": url}
    if expires_in_seconds is not None:
        data["expires_in_seconds"] = expires_in_seconds
    if max_clicks is not None:
        data["max_clicks"] = max_clicks
    if alias is not None:
        data["alias"] = alias
    response = client.post("/shorten", json=data)
    return response


def test_create_with_valid_alias():
    alias = "my-video-123"
    url = "https://example.com/video"
    response = create_short_url(url, expires_in_seconds=3600, max_clicks=5, alias=alias)
    assert response.status_code == 201
    data = response.json()
    assert data["code"] == alias
    assert data["url"] == url
    assert data["expires_in_seconds"] == 3600
    assert data["max_clicks"] == 5


def test_create_with_duplicate_alias():
    alias = "duplicate-alias"
    url1 = "https://example.com/1"
    url2 = "https://example.com/2"

    # First creation should succeed
    response1 = create_short_url(url1, alias=alias)
    assert response1.status_code == 201

    # Second creation with same alias should fail with 409
    response2 = create_short_url(url2, alias=alias)
    assert response2.status_code == 409


def test_create_with_invalid_alias():
    invalid_aliases = ["UPPERCASE", "with space", "special!", "under_score", "", "123$", "CamelCase"]
    url = "https://example.com"
    for alias in invalid_aliases:
        response = create_short_url(url, alias=alias)
        assert response.status_code == 422


def test_redirect_with_alias():
    alias = "redirect-test"
    url = "https://example.com/redirect"
    # Create with alias
    response = create_short_url(url, alias=alias)
    assert response.status_code == 201

    # Redirect using alias
    redirect_response = client.get(f"/{alias}", follow_redirects=False)
    assert redirect_response.status_code == 307
    assert redirect_response.headers["location"] == url


def test_redirect_with_generated_code():
    url = "https://example.com/generated"
    response = create_short_url(url)
    assert response.status_code == 201
    code = response.json()["code"]

    redirect_response = client.get(f"/{code}", follow_redirects=False)
    assert redirect_response.status_code == 307
    assert redirect_response.headers["location"] == url


def test_backward_compatibility_without_alias():
    url = "https://example.com/backward"
    response = create_short_url(url, expires_in_seconds=10, max_clicks=2)
    assert response.status_code == 201
    data = response.json()
    assert "code" in data
    assert data["url"] == url
    assert data["expires_in_seconds"] == 10
    assert data["max_clicks"] == 2

    code = data["code"]

    # Redirect twice
    for _ in range(2):
        r = client.get(f"/{code}", follow_redirects=False)
        assert r.status_code == 307
        assert r.headers["location"] == url

    # Third redirect should return 410 (click limit reached)
    r = client.get(f"/{code}", follow_redirects=False)
    assert r.status_code == 410


def test_alias_and_expiration_independent():
    alias = "expire-test"
    url = "https://example.com/expire"
    response = create_short_url(url, expires_in_seconds=1, alias=alias)
    assert response.status_code == 201

    # Redirect immediately should succeed
    r1 = client.get(f"/{alias}", follow_redirects=False)
    assert r1.status_code == 307

    import time
    time.sleep(1.1)  # Wait for expiration

    # Redirect after expiration should return 410
    r2 = client.get(f"/{alias}", follow_redirects=False)
    assert r2.status_code == 410


def test_alias_and_click_limit_independent():
    alias = "clicklimit-test"
    url = "https://example.com/clicklimit"
    response = create_short_url(url, max_clicks=2, alias=alias)
    assert response.status_code == 201

    # Two redirects succeed
    for _ in range(2):
        r = client.get(f"/{alias}", follow_redirects=False)
        assert r.status_code == 307

    # Third redirect returns 410
    r = client.get(f"/{alias}", follow_redirects=False)
    assert r.status_code == 410


def test_create_with_alias_and_no_other_params():
    alias = "simple-alias"
    url = "https://example.com/simple"
    response = create_short_url(url, alias=alias)
    assert response.status_code == 201
    data = response.json()
    assert data["code"] == alias
    assert data["url"] == url
    assert "expires_in_seconds" not in data or data["expires_in_seconds"] is None
    assert "max_clicks" not in data or data["max_clicks"] is None


def test_create_without_alias_and_with_all_params():
    url = "https://example.com/full"
    response = create_short_url(url, expires_in_seconds=100, max_clicks=10)
    assert response.status_code == 201
    data = response.json()
    assert data["code"] != ""
    assert data["url"] == url
    assert data["expires_in_seconds"] == 100
    assert data["max_clicks"] == 10


def test_create_with_alias_uppercase_rejected():
    alias = "InvalidAlias"
    url = "https://example.com"
    response = create_short_url(url, alias=alias)
    assert response.status_code == 422


def test_create_with_alias_with_underscore_rejected():
    alias = "invalid_alias"
    url = "https://example.com"
    response = create_short_url(url, alias=alias)
    assert response.status_code == 422


def test_redirect_unknown_code_returns_404():
    response = client.get("/nonexistentcode", follow_redirects=False)
    assert response.status_code == 404
