from __future__ import annotations

import os
from pathlib import Path
from typing import Annotated, TypedDict

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

bearer_scheme = HTTPBearer(auto_error=False)


class AuthenticatedUser(TypedDict):
    uid: str
    email: str | None
    name: str | None


def _firebase_admin_app():
    try:
        from firebase_admin import credentials, get_app, initialize_app
    except ImportError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Firebase Admin SDK is not installed. Install the unified backend requirements.",
        ) from exc

    try:
        return get_app()
    except ValueError:
        pass

    credential_path = (
        os.getenv("FIREBASE_SERVICE_ACCOUNT_PATH")
        or os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    )
    if not credential_path:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "Firebase Admin credentials are not configured. Set "
                "FIREBASE_SERVICE_ACCOUNT_PATH or GOOGLE_APPLICATION_CREDENTIALS."
            ),
        )

    path = Path(credential_path).expanduser().resolve()
    if not path.is_file():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Firebase service-account file was not found: {path}",
        )

    try:
        project_id = os.getenv("FIREBASE_PROJECT_ID")
        options = {"projectId": project_id} if project_id else None
        return initialize_app(credentials.Certificate(str(path)), options=options)
    except (OSError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Firebase Admin could not initialize: {exc}",
        ) from exc


def get_current_user(
    credentials: Annotated[
        HTTPAuthorizationCredentials | None,
        Depends(bearer_scheme),
    ],
) -> AuthenticatedUser:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="A Firebase ID token is required.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        from firebase_admin import auth
        from firebase_admin.exceptions import FirebaseError
    except ImportError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Firebase Admin SDK is not installed.",
        ) from exc

    app = _firebase_admin_app()
    try:
        decoded = auth.verify_id_token(
            credentials.credentials,
            app=app,
            check_revoked=True,
        )
    except auth.ExpiredIdTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Firebase ID token has expired. Sign in again.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
    except auth.InvalidIdTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Firebase ID token is invalid.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
    except FirebaseError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Firebase could not verify the ID token. Check server credentials and connectivity.",
        ) from exc

    uid = decoded.get("uid")
    if not isinstance(uid, str) or not uid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Firebase ID token does not contain a user identity.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    email = decoded.get("email")
    name = decoded.get("name")
    return {
        "uid": uid,
        "email": email if isinstance(email, str) else None,
        "name": name if isinstance(name, str) else None,
    }
