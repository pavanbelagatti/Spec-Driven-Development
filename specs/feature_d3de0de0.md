# URL Shortener API — Feature Specification

## 13. Feature: Health Check Endpoint

### Endpoint

GET /health

### Requirements

- Provide a simple health check endpoint.
- Return HTTP 200 OK.
- Return JSON response exactly: {"status": "ok"}.
- No authentication or parameters required.
- Must not access or modify URL storage.
- Must not affect existing endpoints or features.

### Acceptance Criteria

- GET /health returns HTTP 200.
- Response body is exactly {"status": "ok"}.
- Response Content-Type is application/json.
- No side effects on URL shortening or redirect logic.

### Compatibility

- Must not modify existing endpoints or their behavior.
- Must preserve all existing features and validations.
- Must be compatible with pytest and FastAPI TestClient.

### Edge Cases

- Requests with query parameters or headers to /health still return the same response.
- The endpoint should be lightweight and fast.

---

No changes to existing endpoints or logic.

---