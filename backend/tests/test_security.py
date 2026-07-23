"""Tests for security utilities."""

from backend.core.security import Role, create_access_token, decode_access_token, has_permission


def test_password_hash_roundtrip():
    from backend.core.security import get_password_hash, verify_password

    hashed = get_password_hash("secret123")
    assert verify_password("secret123", hashed)
    assert not verify_password("wrong", hashed)


def test_jwt_roundtrip():
    token = create_access_token("user@test.com", Role.ADMIN)
    payload = decode_access_token(token)
    assert payload["sub"] == "user@test.com"
    assert payload["role"] == "admin"


def test_rbac_permissions():
    assert has_permission(Role.ADMIN, "anything")
    assert has_permission(Role.VIEWER, "documents:read")
    assert not has_permission(Role.VIEWER, "documents:write")
