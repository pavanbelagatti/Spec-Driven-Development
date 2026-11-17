# URL Shortener API — Feature Specification

## Addition: API Version Endpoint

### Endpoint

GET /api/version

### Requirements

- Return HTTP 200 OK.
- Return JSON body exactly: {"version": "1.0.0"}.
- Register this endpoint before the dynamic /{code} route to avoid route conflicts.
- Preserve all existing functionality and routes.

### Acceptance Criteria

- GET /api/version returns HTTP 200.
- Response body is exactly {"version": "1.0.0"}.
- No interference with existing endpoints.

## Compatibility and Edge Cases

- The new endpoint must not override or conflict with existing routes.
- The response must be JSON with Content-Type application/json.
- The endpoint must be accessible at /api/version.
- The endpoint must not require any parameters.
- The endpoint must not affect the behavior of /{code} or other routes.

## Implementation Notes

- Register the GET /api/version route before the dynamic /{code} route in FastAPI.
- Use a simple function returning a dict with the version string.
- Use status code 200 (default for GET).

---

No changes to existing endpoints or behavior.

