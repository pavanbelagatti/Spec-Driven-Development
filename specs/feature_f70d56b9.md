# API Version Endpoint

## Endpoint

GET /api/version

## Requirements

- Return HTTP 200 OK.
- Return JSON body exactly: {"version": "1.0.0"}.
- Register this route before the existing dynamic /{code} redirect route to avoid route conflicts.
- Do not modify existing endpoints or behavior.
- Preserve all existing functionality and backward compatibility.

## Acceptance Criteria

- GET /api/version returns HTTP 200.
- Response JSON is exactly {"version": "1.0.0"}.

## Implementation Notes

- Add the route handler in workspace/app.py before the /{code} route.
- Use FastAPI's standard JSON response.
- No changes to existing tests or features.

## Edge Cases

- None specific; the endpoint is static and simple.

## Compatibility

- Compatible with existing FastAPI app.
- Does not interfere with existing routes.
- Works with pytest and FastAPI TestClient.
