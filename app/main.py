"""
FastAPI application entry point for the pHera BFF service.

This module initializes the API application, configures CORS and registers
routers depending on the deployment mode.

Supported modes:

- beta:
    Lightweight proxy mode used for Beta integration.
    Only health check and BFF endpoints are exposed.
    No persistence or authenticated MVP-only routes are enabled.

- mvp:
    Full application mode with authentication and persistence enabled.
    Additional routes such as scans, history and trends are available.
"""

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from .database import Base, engine
from .config import CORS_ORIGINS, DEPLOYMENT_MODE

from .routers.health import router as health_router
from .routers.auth_dev import router as auth_router
from .routers.scans import router as scans_router
from .routers.history import router as history_router
from .routers.trends import router as trends_router
from .routers.bff import router as bff_router

from .deps import get_current_user
from . import models

app = FastAPI(title="pHera Backend MVP")

if CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[o.strip() for o in CORS_ORIGINS if o.strip()],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Always expose the minimal endpoints required for service availability
# and proxy-based Beta integration.
app.include_router(health_router)
app.include_router(bff_router)

# Enable persistence and authenticated routes only in MVP mode.
if DEPLOYMENT_MODE == "mvp":
    Base.metadata.create_all(bind=engine)

    app.include_router(auth_router)
    app.include_router(scans_router)
    app.include_router(history_router)
    app.include_router(trends_router)

    @app.get("/api/me", tags=["auth"])
    def api_me(user: models.User = Depends(get_current_user)):
        """
        Return information about the currently authenticated user.

        This endpoint is available only in MVP mode and is used to verify
        that the authentication flow is working correctly.
        """
        return {"id": user.id, "sub": user.sub, "email": user.email}