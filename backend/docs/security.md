# Security posture for M-Motors backend

## Authentication and session model

The API uses a bearer JWT (`Authorization: Bearer <token>`) and does not store the access token in a browser cookie. For that reason, the classic cookie-only CSRF model is not sufficient by itself for this application. This project therefore implements a CSRF double-submit flow for state-changing API calls: the server sets a signed CSRF cookie, and the frontend must copy the issued token into the `X-CSRF-Token` header. The header value is compared against the signed cookie value before mutating requests are processed.

The login and registration routes are explicitly exempted from CSRF validation because the browser cannot submit a signed CSRF cookie before the user is authenticated; those routes are used to establish the session state itself.

## Trusted proxy strategy

The backend only trusts `X-Forwarded-For` when the direct peer IP is a configured trusted reverse proxy or local loopback source (for example `127.0.0.1`, `::1`, and the local ASGI test client). This avoids accepting arbitrary client-supplied IP addresses through untrusted proxy headers.

## Rate limiting

The login endpoint applies a fail-closed throttle. After five failed authentication attempts within a 60-second window, the next login attempt returns `429 Too Many Requests` with a `Retry-After` header. Successful authentication clears the counter for that client IP.

## CORS and headers

The application no longer uses a wildcard CORS policy in its default configuration. It restricts allowed origins to the local frontend origins needed for development and can be overridden by environment configuration in production.

The app also sets `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`, `Permissions-Policy`, and a conservative `Content-Security-Policy` at the API layer.

## Secret management

The JWT secret is read exclusively from environment configuration (`SECRET_KEY` or `JWT_SECRET_KEY`). The application refuses to start if the secret is empty or set to a known insecure default value.

## Authorization and IDOR checks

The business-layer authorization rules remain in the application/domain logic, not in middleware. User-owned dossier access checks continue to verify that the authenticated user owns the specific resource before returning or mutating it.
