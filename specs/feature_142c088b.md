# URL Shortener API — Feature Specification

## Addition: API Count Endpoint

### Endpoint

GET /api/count

### Requirements

- Return a JSON object with a single key `total_urls`.
- The value of `total_urls` is the current number of stored shortened URLs in the in-memory dictionary.
- The count must reflect all stored URLs, including those with expiration or click limits.
- The endpoint must not modify any stored data.
- Preserve existing API behavior and endpoints.

### Acceptance Criteria

- Before creating any shortened URL, GET /api/count returns `{"total_urls": 0}`.
- After creating one shortened URL, GET /api/count returns `{"total_urls": 1}`.
- The count increments correctly with each new shortened URL.
- The endpoint returns HTTP 200.
- The response content type is application/json.

### Compatibility

- The new endpoint must not interfere with existing endpoints or features.
- The existing POST /shorten and GET /{code} endpoints remain unchanged.
- The new endpoint is added under the `/api` prefix.

### Edge Cases

- Concurrent requests creating URLs must be reflected accurately in the count.
- Deletion of URLs is not supported; count only increases.
- The count includes URLs regardless of expiration or click limits.

---

## Implementation Notes

- Use the existing in-memory `store` dictionary to count entries.
- Implement the endpoint as a FastAPI GET route.
- Return JSON with `total_urls` key.
- Ensure thread safety by reading the dictionary length atomically.

---

## Summary

Add a new GET /api/count endpoint returning the total number of shortened URLs stored in memory, preserving all existing functionality and API behavior.