"""Demo-grade auth helpers (stdlib only). Passwords are hashed; tokens are
HMAC-signed so they can't be trivially forged. The user's ROLE is always read
from the database, never trusted from the client. Fine for a school project;
production would use bcrypt/argon2 + real JWT."""
from __future__ import annotations
import base64, hashlib, hmac

_SALT = "pharmahub-com244"
_TOKEN_SECRET = "pharmahub-com244-token-secret"


def hash_password(pw: str) -> str:
    return hashlib.sha256((_SALT + pw).encode()).hexdigest()

def verify_password(pw: str, hashed: str) -> bool:
    return hash_password(pw) == hashed


def create_token(username: str) -> str:
    payload = base64.urlsafe_b64encode(username.encode()).decode().rstrip("=")
    sig = hmac.new(_TOKEN_SECRET.encode(), payload.encode(), hashlib.sha256).hexdigest()[:16]
    return f"{payload}.{sig}"

def decode_token(token: str) -> str | None:
    try:
        payload, sig = token.split(".")
        expected = hmac.new(_TOKEN_SECRET.encode(), payload.encode(), hashlib.sha256).hexdigest()[:16]
        if not hmac.compare_digest(sig, expected):
            return None
        pad = "=" * (-len(payload) % 4)
        return base64.urlsafe_b64decode(payload + pad).decode()
    except Exception:
        return None
