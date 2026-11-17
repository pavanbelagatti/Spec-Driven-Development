# URL Shortener API — Feature Specification (Updated with Custom Aliases)

## 1. Overview

Add support for optional custom URL aliases in the existing URL Shortener API.

Users can specify a custom short code (alias) when creating a shortened URL.

The alias must consist only of lowercase letters, numbers, and hyphens.

If no alias is provided, the system generates a unique short code automatically.

Duplicate aliases are rejected with HTTP 409 Conflict.

All existing features (expiration, click limits, redirects) remain unchanged and compatible.


## 2. Technical Requirements (Additions)

- Extend the POST /shorten endpoint to accept an optional `alias` field.
- Validate `alias` to allow only lowercase letters (`a-z`), digits (`0-9`), and hyphens (`-`).
- Reject aliases that are already in use with HTTP 409 Conflict.
- When `alias` is omitted or null, generate codes as before.
- Preserve all existing validation and behavior.


## 3. Feature: Custom URL Alias

### Endpoint

POST /shorten

### Request Body (Extended)

{
  "url": "https://example.com",
  "expires_in_seconds": 3600,
  "max_clicks": 3,
  "alias": "my-video"
}

`alias` is optional.

### Requirements

- Accept an optional `alias` string.
- Validate `alias` matches regex `^[a-z0-9-]+$`.
- Reject invalid aliases with HTTP 422 Unprocessable Entity.
- Reject duplicate aliases with HTTP 409 Conflict.
- Store the alias as the short code if valid and unique.
- If no alias, generate code as before.
- Preserve all other stored data and behavior.

### Response Body

Same as before, with `code` reflecting the alias if provided.

### Acceptance Criteria

- Valid alias returns HTTP 201 with `code` equal to alias.
- Duplicate alias returns HTTP 409.
- Invalid alias returns HTTP 422.
- No alias generates unique code as before.
- Existing clients without alias continue to work.


## 4. Feature: Redirect Short URL (No change)

- Redirect behavior remains unchanged.
- Lookup by alias or generated code.


## 5. Validation

- Alias validation uses Pydantic field validators.
- Alias must be lowercase letters, digits, hyphens only.


## 6. Error Handling

- HTTP 409 Conflict for duplicate alias.
- HTTP 422 Unprocessable Entity for invalid alias.


## 7. Backward Compatibility

- Existing clients without alias parameter continue to work.
- Existing endpoints, response codes, and fields remain unchanged.


## 8. Implementation Notes

- Store alias as key in the in-memory dictionary.
- Ensure thread safety when checking and inserting aliases.
- Use existing locking mechanisms.


## 9. Acceptance Testing

Add tests for:

- Creating URLs with valid aliases.
- Rejecting duplicate aliases.
- Rejecting invalid aliases.
- Redirecting using aliases.
- Creating URLs without alias (auto-generated codes).
- Backward compatibility with existing features.

Use FastAPI TestClient with `follow_redirects=False`.


## 10. Summary

This feature adds optional custom aliases with strict validation and duplicate detection, preserving all existing functionality and compatibility.