# URL Shortener API — Feature Specification Addendum

## New Feature: Short URL Count Endpoint

### Endpoint

GET /api/count

### Requirements

- Return HTTP 200 OK.
- Return JSON with a single field `total_urls`.
- `total_urls` is the current count of all stored short URL entries.
- Count includes all entries regardless of expiration or click limits.
- Register this route before the dynamic `/{code}` route to avoid route conflicts.
- Preserve all existing API behavior and routes.

### Response Body

```json
{
  "total_urls": 123
}
```

### Acceptance Criteria

- GET /api/count returns HTTP 200.
- Response JSON contains `total_urls` as an integer.
- After creating a new short URL via POST /shorten, GET /api/count reflects the incremented count.
- Existing features and tests remain unaffected.

## Compatibility and Edge Cases

- The count includes all stored URLs, including expired and those with click limits.
- The count does not decrement when URLs expire or reach click limits.
- The endpoint must not interfere with the dynamic `/{code}` route.
- The endpoint must be thread-safe and consistent with the in-memory store.

## Implementation Notes

- Implement GET /api/count before the dynamic GET /{code} route in `workspace/app.py`.
- Use the existing in-memory `store` dictionary to count entries.
- Return JSON with `total_urls` equal to `len(store)`.
- Do not modify existing endpoints or their behavior.
- Add three pytest tests in a new test module or existing test suite:
  - Test that GET /api/count returns HTTP 200.
  - Test that the response JSON contains `total_urls` as an integer.
  - Test that after POST /shorten, the count increases by one.

## Summary

This feature adds a simple count endpoint to monitor the total number of shortened URLs stored in memory, without affecting existing functionality or routes.
