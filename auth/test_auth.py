import time

import pytest

from auth.core import (
    register,
    login,
    verify_token,
    AuthError,
)


SECRET = "test-secret"


def test_register_creates_user():
    users = {}
    token = register(users, "alice", "password123", secret=SECRET)
    assert isinstance(token, str)
    assert "." in token
    assert "alice" in users


def test_register_duplicate_user_raises():
    users = {}
    register(users, "alice", "password123", secret=SECRET)
    with pytest.raises(AuthError, match="already exists"):
        register(users, "alice", "password123", secret=SECRET)


def test_login_success():
    users = {}
    register(users, "alice", "password123", secret=SECRET)
    token = login(users, "alice", "password123", secret=SECRET)
    payload = verify_token(token, secret=SECRET)
    assert payload["sub"] == "alice"


def test_login_wrong_password():
    users = {}
    register(users, "alice", "password123", secret=SECRET)
    with pytest.raises(AuthError, match="Invalid"):
        login(users, "alice", "wrong", secret=SECRET)


def test_login_unknown_user():
    users = {}
    with pytest.raises(AuthError, match="Invalid"):
        login(users, "alice", "password123", secret=SECRET)


def test_verify_token_expired():
    users = {}
    register(users, "alice", "password123", secret=SECRET)
    token = login(users, "alice", "password123", secret=SECRET, ttl=-1)
    with pytest.raises(AuthError, match="expired"):
        verify_token(token, secret=SECRET)


def test_verify_token_tampered():
    users = {}
    register(users, "alice", "password123", secret=SECRET)
    token = login(users, "alice", "password123", secret=SECRET)
    with pytest.raises(AuthError, match="Invalid"):
        verify_token(token + "x", secret=SECRET)


def test_verify_token_wrong_secret():
    users = {}
    register(users, "alice", "password123", secret=SECRET)
    token = login(users, "alice", "password123", secret=SECRET)
    with pytest.raises(AuthError, match="Invalid"):
        verify_token(token, secret="other-secret")
