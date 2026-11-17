# URL Shortener API — Feature Specification Addendum

## New Feature: API Version Endpoint

### Endpoint

GET /api/version

### Requirements

- Return HTTP 200 OK.
- Return JSON body exactly: {"version": "1.0.0"}.
- Register this endpoint before the catch-all /{code} route to avoid routing conflicts.
- Preserve all existing functionality and routes.

### Acceptance Criteria

- GET /api/version returns HTTP 200.
- Response JSON is exactly {"version": "1.0.0"}.
- No interference with existing endpoints.

---

## Compatibility and Edge Cases

- The new endpoint must not override or interfere with existing endpoints.
- The response must be JSON with Content-Type application/json.
- The endpoint must be accessible without any parameters.
- The endpoint must be registered before /{code} to prevent route shadowing.

---

## Implementation Notes

- Add a new FastAPI route handler for GET /api/version.
- Return a fixed dictionary {"version": "1.0.0"}.
- Ensure the route is declared before the /{code} route in the source code.

---

## Testing Requirements

- Test that GET /api/version returns HTTP 200.
- Test that the response JSON matches exactly {"version": "1.0.0"}.
- Tests must import `app` from `workspace.app`.
- Tests must use FastAPI TestClient.
- Tests must not affect or depend on other tests.
- Tests must not modify existing tests or functionality.
