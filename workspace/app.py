from fastapi import FastAPI, HTTPException, status
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, field_validator
from typing import Optional
from urllib.parse import urlparse
from datetime import datetime, timedelta
import threading
import re

app = FastAPI()

# In-memory store: code -> {url, expires_at, max_clicks, click_count, lock}
store = {}

# Thread-safe counter for generating unique codes
counter_lock = threading.Lock()
counter = 1

BASE62 = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

CODE_REGEX = re.compile(r'^[a-z0-9-]+$')


def encode_base62(num: int) -> str:
    if num == 0:
        return BASE62[0]
    arr = []
    base = len(BASE62)
    while num > 0:
        num, rem = divmod(num, base)
        arr.append(BASE62[rem])
    arr.reverse()
    return ''.join(arr)


class ShortenRequest(BaseModel):
    url: str
    expires_in_seconds: Optional[int] = None
    max_clicks: Optional[int] = None
    alias: Optional[str] = None

    @field_validator('url')
    @classmethod
    def validate_url(cls, v):
        if not v or not isinstance(v, str):
            raise ValueError('URL must be a non-empty string')
        parsed = urlparse(v)
        if parsed.scheme not in ('http', 'https'):
            raise ValueError('URL scheme must be http or https')
        if not parsed.hostname:
            raise ValueError('URL must have a hostname')
        return v

    @field_validator('expires_in_seconds')
    @classmethod
    def validate_expires_in_seconds(cls, v):
        if v is not None:
            if not isinstance(v, int) or v <= 0:
                raise ValueError('expires_in_seconds must be a positive integer')
        return v

    @field_validator('max_clicks')
    @classmethod
    def validate_max_clicks(cls, v):
        if v is not None:
            if not isinstance(v, int) or v <= 0:
                raise ValueError('max_clicks must be a positive integer')
        return v

    @field_validator('alias')
    @classmethod
    def validate_alias(cls, v):
        if v is None:
            return v
        if not isinstance(v, str) or not v:
            raise ValueError('alias must be a non-empty string if provided')
        if not CODE_REGEX.fullmatch(v):
            raise ValueError('alias must contain only lowercase letters, digits, and hyphens')
        return v


@app.get('/health')
def health_check():
    return {"status": "ok"}


@app.get('/api/version')
def api_version():
    return {"version": "1.0.0"}


@app.get('/api/count')
def api_count():
    # Return total number of stored short URLs
    total = len(store)
    return {"total_urls": total}


@app.post('/shorten', status_code=status.HTTP_201_CREATED)
def shorten(req: ShortenRequest):
    global counter

    # Prepare expiration datetime
    expires_at = None
    if req.expires_in_seconds is not None:
        expires_at = datetime.utcnow() + timedelta(seconds=req.expires_in_seconds)

    # Prepare entry data
    entry = {
        'url': req.url,
        'expires_at': expires_at,
        'max_clicks': req.max_clicks,  # None means unlimited
        'click_count': 0,
        'lock': threading.Lock()
    }

    with counter_lock:
        if req.alias is not None:
            code = req.alias
            if code in store:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Alias already in use')
            store[code] = entry
        else:
            # Generate unique code
            while True:
                code = encode_base62(counter)
                counter += 1
                if code not in store:
                    store[code] = entry
                    break

    # Build response preserving backward compatibility
    response = {
        'code': code,
        'url': req.url,
        'expires_in_seconds': req.expires_in_seconds
    }
    # Include max_clicks only if provided
    if req.max_clicks is not None:
        response['max_clicks'] = req.max_clicks

    return response


@app.get('/api/stats/{code}')
def get_stats(code: str):
    entry = store.get(code)
    if entry is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Code not found')

    return {
        'code': code,
        'url': entry['url'],
        'click_count': entry['click_count']
    }


@app.get('/api/welcome')
def api_welcome():
    return {"message": "Welcome to LinkForge"}


@app.get('/{code}')
def redirect(code: str):
    entry = store.get(code)
    if entry is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Code not found')

    expires_at = entry['expires_at']
    if expires_at is not None and datetime.utcnow() > expires_at:
        raise HTTPException(status_code=status.HTTP_410_GONE, detail='Code expired')

    max_clicks = entry['max_clicks']

    # Increment click count safely and check limits atomically
    with entry['lock']:
        click_count = entry['click_count']
        if max_clicks is not None and click_count >= max_clicks:
            raise HTTPException(status_code=status.HTTP_410_GONE, detail='Click limit reached')
        entry['click_count'] += 1

    return RedirectResponse(url=entry['url'], status_code=status.HTTP_307_TEMPORARY_REDIRECT)
