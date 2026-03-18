"""
Application configuration module.

This module centralizes all environment-based settings used by the service.

Key concepts:

- Environment variables are used to configure the service behavior.
- Defaults are provided where possible for local development.

Important settings:

- DEPLOYMENT_MODE:
    Controls how the service behaves:
    - "beta" → proxy-only mode (no authentication, no persistence)
    - "mvp" → full mode (authentication + database persistence)

- RAG_BASE_URL:
    Base URL of the external RAG backend service.

- RAG_API_KEY:
    API key used in MVP mode for authenticated communication with RAG.

- ZITADEL_*:
    Configuration for OIDC authentication (used in MVP mode).
"""

import os


def get_env(name: str, default: str | None = None) -> str | None:
    """
    Helper function to read environment variables with an optional default.
    """
    return os.getenv(name, default)


# Database
DATABASE_URL = get_env("DATABASE_URL")

# Zitadel OIDC (OIDC discovery + JWKS will be resolved from this issuer)
ZITADEL_ISSUER = (get_env("ZITADEL_ISSUER") or "https://phera-dev-s43qhq.us1.zitadel.cloud").rstrip("/")

# Audience is optional. If you don't know it yet, keep it empty and we won't enforce it.
ZITADEL_AUDIENCE = get_env("ZITADEL_AUDIENCE")  # optional

# Dev-only token secret (for local testing via /auth/dev-token)
DEV_JWT_SECRET = get_env("DEV_JWT_SECRET", "dev-only-secret-change-me")

# CORS
CORS_ORIGINS = (
    (get_env("CORS_ORIGINS", "") or "").split(",")
    if get_env("CORS_ORIGINS")
    else []
)

# Controls service behavior: "beta" (proxy-only) or "mvp" (full mode)
DEPLOYMENT_MODE = (get_env("DEPLOYMENT_MODE", "beta") or "beta").strip().lower()

# RAG backend configuration
RAG_API_KEY = get_env("RAG_API_KEY", "")
RAG_BASE_URL = get_env(
    "RAG_BASE_URL",
    "https://phera-rag-beta-52458262724.europe-west10.run.app",
)