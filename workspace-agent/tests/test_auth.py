from __future__ import annotations

from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from agent_service.auth import get_current_user


def test_firebase_id_token_is_required() -> None:
    try:
        get_current_user(None)
    except HTTPException as error:
        assert error.status_code == 401
        assert error.detail == "A Firebase ID token is required."
    else:
        raise AssertionError("An absent Firebase ID token must be rejected.")


def test_missing_firebase_admin_credentials_is_explicit(monkeypatch) -> None:
    monkeypatch.delenv("FIREBASE_SERVICE_ACCOUNT_PATH", raising=False)
    monkeypatch.delenv("GOOGLE_APPLICATION_CREDENTIALS", raising=False)

    credentials = HTTPAuthorizationCredentials(
        scheme="Bearer",
        credentials="not-a-real-token",
    )
    try:
        get_current_user(credentials)
    except HTTPException as error:
        assert error.status_code == 503
        assert "Firebase Admin credentials are not configured" in error.detail
    else:
        raise AssertionError("Missing server credentials must be reported.")
