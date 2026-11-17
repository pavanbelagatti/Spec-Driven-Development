
# URL Shortener API — Feature Specification

## 1. Overview

Build a URL Shortener REST API using Python and FastAPI.

The application must allow users to create shortened URLs,
redirect visitors to original URLs, configure expiration times,
and optionally restrict the number of redirects.

The implementation must satisfy all acceptance criteria below.

## 2. Technical Requirements

- Use Python and FastAPI.
- Use Pydantic for request validation.
- Use an in-memory dictionary for URL storage.
- Do not require an external database.
- Expose the FastAPI application as `app` in workspace/app.py.
- Use HTTP redirects for valid shortened URLs.
- Preserve existing API behavior when adding features.
- Ensure compatibility with pytest and FastAPI TestClient.

## 3. Feature: Create Short URL

### Endpoint

POST /shorten

### Request Body

{
  "url": "https://example.com",
  "expires_in_seconds": 3600,
  "max_clicks": 3
}

### Requirements

- Accept an original URL.
- Accept an expiration duration in seconds.
- Accept an optional maximum click limit.
- Generate a unique short code for each request.
- Store the URL, creation time, expiration time,
  click limit, and current click count.
- Initialize the click count to zero.
- Return HTTP 201 Created when successful.

### Response Body

{
  "code": "abc123",
  "url": "https://example.com",
  "expires_in_seconds": 3600
}

The response may include additional metadata.

### Acceptance Criteria

- A valid URL returns HTTP 201.
- The response contains a non-empty `code`.
- Every newly created URL receives a unique code.
- The original URL is preserved.
- Existing clients can omit `max_clicks`.
- The response remains backward compatible.

## 4. Feature: URL Validation

### Requirements

- Accept only HTTP and HTTPS URLs.
- Reject malformed URLs.
- Reject empty URL strings.
- Reject unsupported schemes such as FTP.
- Validate requests using Pydantic.

### Acceptance Criteria

- `https://example.com` is accepted.
- `http://example.com` is accepted.
- `not-a-url` returns HTTP 422.
- `hello` returns HTTP 422.
- An empty URL returns HTTP 422.
- `ftp://example.com` returns HTTP 422.

## 5. Feature: Redirect Short URL

### Endpoint

GET /{code}

### Requirements

- Look up the short code in storage.
- Return HTTP 404 if the code does not exist.
- Return an HTTP redirect to the original URL
  when the code is valid.
- Include the original URL in the Location header.
- Support HTTP 307 Temporary Redirect.
- Preserve the original URL exactly.

### Acceptance Criteria

- A valid code redirects successfully.
- The Location header matches the original URL.
- An unknown code returns HTTP 404.

## 6. Feature: URL Expiration

### Requirements

- Support `expires_in_seconds` in the creation request.
- Calculate expiration based on creation time.
- Check expiration before every redirect.
- Expired URLs must not redirect.
- Return HTTP 410 Gone for expired URLs.
- Expiration behavior must remain independent
  of click-limit behavior.

### Acceptance Criteria

- A URL with `expires_in_seconds=1` expires
  after approximately one second.
- Requesting an expired URL returns HTTP 410.
- An expired URL must not increment its click count.
- A URL that has not expired can still redirect
  if its click limit has not been reached.

## 7. Feature: Maximum Click Limits

### Request Parameter

`max_clicks` (optional integer)

### Requirements

- Accept an optional `max_clicks` parameter
  when creating a shortened URL.
- If omitted or null, redirects are unlimited.
- If supplied, `max_clicks` must be a positive integer.
- Reject zero and negative click limits.
- Initialize `click_count` to zero.
- Increment `click_count` only after a successful
  redirect has been authorized.
- Allow exactly `max_clicks` successful redirects.
- Once the click limit has been reached,
  return HTTP 410 Gone for subsequent requests.
- Do not increment the counter for rejected requests.
- The limit must apply independently to each short code.

### Acceptance Criteria

#### Scenario A: Three-Click Limit

Given a shortened URL with `max_clicks=3`:

- First request returns HTTP 307.
- Second request returns HTTP 307.
- Third request returns HTTP 307.
- Fourth request returns HTTP 410.

#### Scenario B: Single-Click Limit

Given a shortened URL with `max_clicks=1`:

- First request returns HTTP 307.
- Second request returns HTTP 410.

#### Scenario C: Invalid Limits

- `max_clicks=0` returns HTTP 422.
- `max_clicks=-1` returns HTTP 422.
- `max_clicks=-5` returns HTTP 422.

#### Scenario D: Unlimited Redirects

Given a shortened URL without `max_clicks`:

- The URL supports unlimited redirects.
- Five consecutive requests must succeed.
- Existing expiration rules still apply.

## 8. Redirect Decision Logic

For every GET /{code} request, execute these
checks in the following order:

1. Look up the short code.
2. If the code does not exist, return HTTP 404.
3. If the URL has expired, return HTTP 410.
4. If max_clicks is not null and
   click_count >= max_clicks, return HTTP 410.
5. Increment click_count by one.
6. Return HTTP 307 with the original URL
   in the Location header.

Important:

The click-limit comparison must use >=,
not >, to prevent an extra redirect.

## 9. Backward Compatibility

The new click-limit feature must not break
the original URL Shortener API.

The following functionality must continue working:

- Creating shortened URLs.
- Validating URLs.
- Redirecting to original URLs.
- Expiring URLs.
- Rejecting unknown short codes.
- Creating URLs without max_clicks.

Do not rename existing endpoints.

Do not change existing HTTP response codes.

Do not remove existing response fields.

## 10. Acceptance Testing

The implementation must pass all tests in:

tests/test_acceptance.py

The test suite validates:

- URL creation.
- URL redirection.
- Invalid URL handling.
- URL expiration.
- Three-click limit.
- Single-click limit.
- Invalid click limits.
- Unlimited redirects.
- Unknown short codes.

All 14 pytest cases must pass.

Do not modify the acceptance tests to make
the implementation pass.

Fix the application code instead.

## 11. Definition of Done

The feature is complete only when:

- The FastAPI application starts successfully.
- All existing functionality is preserved.
- Click limits work as specified.
- Invalid limits return HTTP 422.
- Expired URLs return HTTP 410.
- Unknown codes return HTTP 404.
- All 14 acceptance tests pass.
- No manual changes to tests are required.
- The implementation is saved in workspace/app.py.

## 12. Implementation Constraints

- Keep the application simple and readable.
- Avoid unnecessary dependencies.
- Do not introduce a database.
- Do not modify files outside workspace/app.py.
- Do not bypass validation.
- Do not hardcode test-specific responses.
- Do not remove existing features.
- Use Pydantic V2 field validators where appropriate.

The specification is the source of truth.

Generated code must satisfy the specification,
not the other way around.