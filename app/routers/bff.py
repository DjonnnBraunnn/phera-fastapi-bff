"""
BFF (Backend-for-Frontend) router.

This module exposes the /api/analyze endpoint, which forwards requests
to the external RAG backend service.

Flow:
Client (Frontend / Node backend) → FastAPI BFF → RAG backend

Behavior depends on DEPLOYMENT_MODE:

- Beta mode:
    - No authentication
    - No persistence
    - Acts as a simple proxy
    - Forwards request directly to RAG API

- MVP mode:
    - Adds authentication headers (API key and optional user context)
    - Can be extended with persistence and user tracking

This design allows a single service to support both lightweight testing (Beta)
and production-ready flows (MVP).
"""

from typing import Any

import httpx
from fastapi import APIRouter, Body, Depends, HTTPException

from .. import config
from ..deps import get_current_user_optional

router = APIRouter(prefix="/api", tags=["bff"])


@router.post("/analyze")
async def analyze(
    payload: dict[str, Any] = Body(...),
    user=Depends(get_current_user_optional),
):
    """
    Handles analysis requests and forwards them to the RAG backend.

    Flow:
    Client → BFF → RAG backend → BFF → Client

    In Beta mode:
        - Request is forwarded without authentication
        - No data is stored

    In MVP mode:
        - API key is attached
        - User context is optionally included

    Args:
        payload: JSON request body containing analysis input
        user: Optional authenticated user (if available)

    Returns:
        JSON response from the RAG backend.
    """

    headers: dict[str, str] = {}

    # Add authentication headers only in MVP mode
    if config.DEPLOYMENT_MODE == "mvp":
        if not config.RAG_API_KEY:
            raise HTTPException(status_code=500, detail="RAG_API_KEY not configured")
        headers["X-API-Key"] = config.RAG_API_KEY
        if user:
            headers["X-User-Id"] = user.sub

    rag_url = f"{config.RAG_BASE_URL.rstrip('/')}/api/v1/query"

    try:
        async with httpx.AsyncClient(timeout=60) as client:
            # Forward request to external RAG backend service
            response = await client.post(rag_url, json=payload, headers=headers)
            return response.json()
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=f"Failed to reach RAG backend: {exc}")