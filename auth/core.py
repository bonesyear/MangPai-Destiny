"""Minimal JWT-based authentication using only the Python standard library."""

import base64
import hashlib
import hmac
import json
import secrets
import time


class AuthError(Exception):
    """Raised for all authentication failures."""


ALGORITHM = "HS256"
_HASH_ITERATIONS = 100_000
_SALT_BYTES = 16


def _b64encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _b64decode(data: str) -> bytes:
    pad = -len(data) % 4
    return base64.urlsafe_b64decode(data + ("=" * pad))


def _hash_password(password: str, salt: str) -> str:
    return hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("ascii"),
        _HASH_ITERATIONS,
    ).hex()


def _sign(header_b64: str, payload_b64: str, secret: str) -> str:
    msg = f"{header_b64}.{payload_b64}".encode("ascii")
    return _b64encode(hmac.new(secret.encode("ascii"), msg, hashlib.sha256).digest())


def _encode_jwt(payload: dict, secret: str) -> str:
    header = {"alg": ALGORITHM, "typ": "JWT"}
    header_b64 = _b64encode(json.dumps(header, separators=(",", ":")).encode("utf-8"))
    payload_b64 = _b64encode(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
    signature = _sign(header_b64, payload_b64, secret)
    return f"{header_b64}.{payload_b64}.{signature}"


def _decode_jwt(token: str, secret: str) -> dict:
    try:
        header_b64, payload_b64, signature = token.split(".")
        expected = _sign(header_b64, payload_b64, secret)
        if not hmac.compare_digest(signature, expected):
            raise AuthError("Invalid token signature")
        payload = json.loads(_b64decode(payload_b64).decode("utf-8"))
    except Exception as exc:
        raise AuthError("Invalid token") from exc

    if payload.get("exp", float("inf")) < time.time():
        raise AuthError("Token expired")

    return payload


def register(users: dict, username: str, password: str, *, secret: str) -> str:
    """Register a new user and return a JWT."""
    if not username or not password:
        raise AuthError("Username and password are required")
    if username in users:
        raise AuthError("User already exists")

    salt = secrets.token_hex(_SALT_BYTES)
    users[username] = {
        "salt": salt,
        "hash": _hash_password(password, salt),
    }
    return _encode_jwt({"sub": username, "iat": int(time.time())}, secret)


def login(
    users: dict,
    username: str,
    password: str,
    *,
    secret: str,
    ttl: int = 3600,
) -> str:
    """Authenticate a user and return a JWT."""
    user = users.get(username)
    if user is None:
        raise AuthError("Invalid credentials")
    if user["hash"] != _hash_password(password, user["salt"]):
        raise AuthError("Invalid credentials")

    now = int(time.time())
    return _encode_jwt(
        {"sub": username, "iat": now, "exp": now + ttl},
        secret,
    )


def verify_token(token: str, *, secret: str) -> dict:
    """Verify a JWT and return its payload."""
    return _decode_jwt(token, secret)
