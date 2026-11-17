
import time
import uuid

import pytest
from fastapi.testclient import TestClient

from workspace.app import app


client = TestClient(app)


def create_short_url(
    url=None,
    expires_in_seconds=3600,
    max_clicks=None,
):
    """Create a shortened URL for testing."""

    if url is None:
        url = f"https://example.com/{uuid.uuid4()}"

    payload = {
        "url": url,
        "expires_in_seconds": expires_in_seconds,
    }

    if max_clicks is not None:
        payload["max_clicks"] = max_clicks

    return client.post("/shorten", json=payload)


def get_redirect(code):
    """Request a short URL without following redirects."""

    return client.get(
        f"/{code}",
        follow_redirects=False,
    )


# -----------------------------------------
# TEST 1: Create a shortened URL
# -----------------------------------------

def test_create_short_url():
    response = create_short_url()

    assert response.status_code == 201
    assert "code" in response.json()
    assert response.json()["code"]


# -----------------------------------------
# TEST 2: Redirect to original URL
# -----------------------------------------

def test_redirect():
    original_url = "https://example.com/redirect-test"

    response = create_short_url(url=original_url)

    assert response.status_code == 201

    code = response.json()["code"]

    redirect = get_redirect(code)

    assert redirect.status_code in (301, 302, 303, 307, 308)
    assert redirect.headers["location"] == original_url


# -----------------------------------------
# TEST 3: Reject invalid URLs
# -----------------------------------------

@pytest.mark.parametrize(
    "invalid_url",
    [
        "not-a-url",
        "hello",
        "",
        "ftp://example.com",
    ],
)
def test_invalid_urls(invalid_url):
    response = create_short_url(url=invalid_url)

    assert response.status_code == 422


# -----------------------------------------
# TEST 4: Expired URL returns HTTP 410
# -----------------------------------------

def test_expired_url():
    response = create_short_url(
        expires_in_seconds=1,
    )

    assert response.status_code == 201

    code = response.json()["code"]

    time.sleep(1.2)

    redirect = get_redirect(code)

    assert redirect.status_code == 410


# -----------------------------------------
# TEST 5: Click limit allows 3 redirects
# -----------------------------------------

def test_click_limit():
    response = create_short_url(
        max_clicks=3,
    )

    assert response.status_code == 201

    code = response.json()["code"]

    for attempt in range(3):
        redirect = get_redirect(code)

        assert redirect.status_code in (
            301, 302, 303, 307, 308
        ), f"Redirect {attempt + 1} failed"

    fourth_redirect = get_redirect(code)

    assert fourth_redirect.status_code == 410


# -----------------------------------------
# TEST 6: Reject invalid click limits
# -----------------------------------------

@pytest.mark.parametrize(
    "invalid_limit",
    [0, -1, -5],
)
def test_invalid_click_limit(invalid_limit):
    response = create_short_url(
        max_clicks=invalid_limit,
    )

    assert response.status_code == 422


# -----------------------------------------
# TEST 7: Unlimited redirects
# -----------------------------------------

def test_unlimited_redirects():
    response = create_short_url()

    assert response.status_code == 201

    code = response.json()["code"]

    for _ in range(5):
        redirect = get_redirect(code)

        assert redirect.status_code in (
            301, 302, 303, 307, 308
        )


# -----------------------------------------
# TEST 8: Click limit of exactly one
# -----------------------------------------

def test_single_click_limit():
    response = create_short_url(
        max_clicks=1,
    )

    assert response.status_code == 201

    code = response.json()["code"]

    first = get_redirect(code)
    second = get_redirect(code)

    assert first.status_code in (
        301, 302, 303, 307, 308
    )

    assert second.status_code == 410


# -----------------------------------------
# TEST 9: Unknown short code
# -----------------------------------------

def test_unknown_code():
    response = get_redirect(
        "nonexistent-code-123456789"
    )

    assert response.status_code == 404