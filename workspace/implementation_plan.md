1. Extend the ShortenRequest model to include an optional max_clicks field with validation to ensure it is either None or a positive integer (>0).
2. Update the in-memory store to save max_clicks and initialize click_count to zero for each shortened URL.
3. Modify the /shorten POST endpoint to handle max_clicks, validate it, and include it in the stored data and response.
4. Update the GET /{code} endpoint to implement the redirect decision logic:
   - Return 404 if code not found.
   - Return 410 if expired.
   - Return 410 if max_clicks is set and click_count >= max_clicks.
   - Otherwise, increment click_count and return 307 redirect.
5. Preserve existing behavior and response fields for backward compatibility.
6. Use Pydantic V2 style validators (@field_validator) for validation.
7. Ensure thread safety when incrementing click_count by using a threading.Lock per entry or a global lock.
8. Keep the code simple and readable, no external dependencies beyond FastAPI and standard library.
9. Do not modify existing endpoints or response codes.
10. Return the additional fields in the response as allowed by the spec (e.g., max_clicks if present).

This plan satisfies all requirements and acceptance criteria, including expiration, click limits, validation, and backward compatibility.
