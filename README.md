# pHera FastAPI BFF

FastAPI-based **Backend-for-Frontend (BFF) microservice** used in the pHera architecture.

This service acts as a dedicated integration layer between the application backend and AI / RAG services.

It is designed to support **two runtime modes**:

- **Beta mode** → lightweight proxy (no auth, no persistence)
- **MVP mode** → authenticated + persistence-enabled backend

The same codebase can switch between these modes via configuration.

---

# Architecture

High-level architecture:

Frontend  
↓  
Node Backend / API Layer  
↓  
FastAPI BFF Service  
↓  
RAG / AI Backend  

The BFF service is responsible for:

- forwarding requests to RAG
- handling authentication (MVP mode)
- attaching API keys
- forwarding user context
- isolating AI logic from the main backend

This separation allows independent scaling and reuse across projects.

---

# Supported Modes

## Beta mode

`Frontend / Node Backend → BFF → RAG beta backend`

Behavior:

- no authentication
- no database usage
- no persistence
- acts as a pure proxy
- request body is forwarded directly

Used for fast integration and testing.

---

## MVP mode

`Frontend / Node Backend → BFF → RAG backend`

Behavior:

- validates JWT (Zitadel)
- attaches `X-API-Key`
- attaches `X-User-Id` (if available)
- enables persistence (PostgreSQL)
- enables additional API routes

Used for production-ready flows.

---

# API Endpoints

## Always available

- `GET /health` — health check
- `POST /api/analyze` — forward request to RAG backend

## MVP-only endpoints

- `POST /auth/dev-token` — local JWT generation
- `GET /api/me` — current user info
- `POST /scans` — create scan
- `GET /history` — user history
- `GET /trends` — aggregated stats

---

# Environment Configuration

Configuration is provided via `.env`.

Important variables:

- `DATABASE_URL`
- `ZITADEL_ISSUER`
- `ZITADEL_AUDIENCE`
- `DEV_JWT_SECRET`
- `CORS_ORIGINS`
- `DEPLOYMENT_MODE`
- `RAG_BASE_URL`
- `RAG_API_KEY`

## Deployment Mode

```
DEPLOYMENT_MODE=beta
```

or

```
DEPLOYMENT_MODE=mvp
```

---

# How Mode Switching Works

The service dynamically enables/disables features based on `DEPLOYMENT_MODE`:

| Feature            | Beta | MVP |
|-------------------|------|-----|
| /api/analyze      | ✅   | ✅  |
| Authentication    | ❌   | ✅  |
| Database          | ❌   | ✅  |
| /history          | ❌   | ✅  |
| /trends           | ❌   | ✅  |

---

# Local Development

Run with Docker:

```
docker compose up --build
```

Service will be available at:

```
http://localhost:8000
```

Swagger:

```
http://localhost:8000/docs
```

---

# Testing

## Test Beta flow

1. Set:

```
DEPLOYMENT_MODE=beta
```

2. Call:

```
POST /api/analyze
```

---

## Test MVP flow

1. Set:

```
DEPLOYMENT_MODE=mvp
```

2. Generate token:

```
POST /auth/dev-token
```

3. Call:

```
GET /api/me
POST /scans
GET /history
GET /trends
```

---

# Example Analyze Request

```
{
  "ph_value": 4.5,
  "age": 30,
  "diagnoses": [],
  "symptoms": {
    "vulva_vagina": ["itching"]
  }
}
```

---

# Repository Purpose

Reusable AI integration layer for the pHera platform.

---

# Status

Current stage: **Beta + MVP ready**
