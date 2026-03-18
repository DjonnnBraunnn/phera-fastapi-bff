"""
Shared dependency module for the FastAPI service.

This file provides reusable dependencies for routes, mainly around:

- database session handling
- authenticated user resolution
- optional user context in MVP mode

Behavior depends on DEPLOYMENT_MODE:

- beta:
    - no authentication
    - no persistence
    - database access is disabled

- mvp:
    - authentication is enabled
    - user context is extracted from JWT
    - database persistence is available
"""

from fastapi import Header, HTTPException, status

from .config import DEPLOYMENT_MODE


def get_db():
    """
    Provide a database session for MVP mode routes.

    In beta mode, database access is disabled because the service acts only
    as a lightweight proxy and does not persist any data.
    """
    # Database sessions are only needed for authenticated / persistent MVP routes.
    if DEPLOYMENT_MODE != "mvp":
        yield None
        return

    from .database import SessionLocal

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    authorization: str | None = Header(default=None),
    db=None,
):
    """
    Resolve the current authenticated user from the Authorization header.

    This dependency is intended for protected MVP routes. It validates the JWT,
    extracts user identity fields (`sub`, `email`), and ensures a matching user
    exists in the database.

    In beta mode this dependency is disabled and always returns 401 because
    authentication is not part of the Beta flow.
    """
    if DEPLOYMENT_MODE != "mvp":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication is disabled in beta mode",
        )

    from .auth import verify_token
    from . import models

    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing Bearer token")

    token = authorization.split(" ", 1)[1].strip()
    payload = verify_token(token)

    sub = payload.get("sub")
    email = payload.get("email")
    if not sub:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token missing 'sub'")

    if db is None:
        raise HTTPException(status_code=500, detail="Database session is not available")

    # Create the user record on first authenticated access if it does not exist yet.
    user = db.query(models.User).filter(models.User.sub == sub).first()
    if not user:
        user = models.User(sub=sub, email=email or "")
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


def get_current_user_optional(
    authorization: str | None = Header(default=None),
    db=None,
):
    """
    Resolve the current user if authentication information is available.

    This dependency is useful for routes such as the BFF endpoint where:
    - beta mode should work without authentication
    - mvp mode may enrich requests with user context when a valid JWT exists

    Returns:
        User object if authentication succeeds in MVP mode, otherwise None.
    """
    if DEPLOYMENT_MODE != "mvp":
        return None

    from .auth import verify_token
    from . import models

    if not authorization or not authorization.lower().startswith("bearer "):
        return None
    try:
        token = authorization.split(" ", 1)[1].strip()
        payload = verify_token(token)
        sub = payload.get("sub")
        email = payload.get("email")
        if not sub or db is None:
            return None

        # Reuse existing user context or create it lazily on first valid request.
        user = db.query(models.User).filter(models.User.sub == sub).first()
        if not user:
            user = models.User(sub=sub, email=email or "")
            db.add(user)
            db.commit()
            db.refresh(user)
        return user
    except Exception:
        # Optional auth should never break the request flow.
        return None