# URL Shortener API — Additional Feature Specification

## New Feature: Get URL Statistics

### Endpoint

GET /api/stats/{code}

### Requirements

- Return HTTP 200 with JSON body containing:
  - `code`: the short code string
  - `url`: the original URL string
  - `click_count`: the current number of successful redirects
- Do not increment `click_count` when this endpoint is called.
- Return HTTP 404 if the code does not exist in storage.
- Preserve existing API behavior and response codes.
- Register this endpoint before the catch-all GET /{code} to avoid routing conflicts.

### Response Body Example

```json
{
  "code": "abc123",
  "url": "https://example.com",
  "click_count": 0
}
```

### Acceptance Criteria

- Requesting stats for a known code returns HTTP 200 with correct data.
- The initial `click_count` is zero immediately after creation.
- After one successful redirect (GET /{code} with follow_redirects=False), `click_count` increments by one.
- Requesting stats for an unknown code returns HTTP 404.
- The new endpoint does not affect existing redirect or shorten endpoints.

### Compatibility

- Must not change existing endpoints or their behavior.
- Must not increment click counts on stats requests.
- Must be compatible with pytest and FastAPI TestClient.

### Edge Cases

- Stats requested for expired or click-limit reached codes still return current `click_count` and URL.
- Stats requested for codes with aliases behave identically.
- Concurrent requests to stats and redirects do not cause race conditions.

---

# Implementation Notes

- Add a new GET endpoint `/api/stats/{code}` before the existing `/{code}` route.
- Use the existing in-memory `store` dictionary to retrieve data.
- Return HTTP 404 if code not found.
- Return JSON with `code`, `url`, and `click_count`.
- Do not modify `click_count` or any other state.

