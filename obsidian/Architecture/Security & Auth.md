# Security & Authentication

## Overview

The LiveKit MCP Server integrates with **Mantra Auth** (`~/mantra-auth`), an OAuth 2.1 authorization server.

## Authentication Strategies

### 1. Shared JWT Verification (Primary / High Performance)
- **Algorithm:** `HS256`
- **Secret:** Shared `JWT_SECRET` (configured via `.env` or secrets manager)
- **Validation:**
  - Expiration timestamp (`exp`)
  - Token type (`token_type == 'access_token'`)
  - Optional Issuer (`iss`) matching `AUTH_SERVER_URL`
  - Optional Audience (`aud`)
- **Transport Mechanisms Supported:**
  - Header: `Authorization: Bearer <token>`
  - Query Parameter: `?token=<token>` (useful for browser/client EventSource connections where custom headers are unsupported)

### 2. OAuth Introspection (Secondary / Remote Token Verification)
- Endpoint: `POST ${AUTH_SERVER_URL}/api/oauth/introspect`
- Request payload: `token=<jwt_or_opaque_token>&token_type_hint=access_token`
- Evaluates `active: true` and verifies scopes (`client_id`, `scope`, `sub`).

## Error Handling
- Missing token: `401 Unauthorized` with `{"error": "unauthorized", "error_description": "Authorization token required"}` (dev/non-production allows anonymous `anonymous-dev` state instead)
- Invalid/Expired token: `401 Unauthorized` with `{"error": "invalid_token", "error_description": "Token is invalid or expired"}`
- Unprotected routes: `/health`, `/`, `/docs`, `/openapi.json`, `/favicon.ico`, `/robots.txt`, `/sitemap.xml`, `/api/dev/token`, `/api/dev/check-db`, `/api/dev/check-lkt` bypass authentication.

## Verification Order (`AuthMiddleware`)
1. Local HS256 JWT verify (`jwt_secret`, optional `JWT_ISSUER`/`MCP_ISSUER_URL` issuer, `JWT_AUDIENCE` audience).
2. On local failure, remote RFC 7662 introspection via `AuthClient` (`POST ${AUTH_SERVER_URL}/api/oauth/introspect`).
