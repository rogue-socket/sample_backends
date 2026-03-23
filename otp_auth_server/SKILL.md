---
name: OTP Auth Server
description: OTP-based authentication with access and refresh token sessions.
port: 8004
tech: FastAPI
---

# OTP Auth Server

Authentication API running on port 8004. Provides OTP-based login, session token management with access/refresh tokens, and user session endpoints.

## When to Use

- Testing OTP-based authentication flows
- Building login/logout UI for passwordless auth
- Testing session token refresh and expiry
- Simulating multi-device session management

## Core Workflows

### Request OTP
POST /auth/request-otp with {identifier} (email or phone) → returns otp_code and expires_at. Code valid for 300 seconds.

### Verify OTP and Login
POST /auth/verify-otp with {identifier, otp_code} → if valid, returns user object and tokens: access_token (expires 900s), refresh_token (expires 7d), plus expiry timestamps.

### Use Access Token
POST /auth/me with {access_token} → returns user object and access_token expiry. Valid as long as access_token is not expired.

### Refresh Session
POST /auth/refresh with {refresh_token} → issues new access_token and new refresh_token if refresh_token is valid and not expired.

### Logout
POST /auth/logout with optional {refresh_token} → revokes refresh token and all associated access tokens.

### Reset State
POST /auth/reset → clears all users, OTP codes, and sessions (dev/testing only).

## Health Check

GET /health returns service health status.

## Token Lifetimes

- OTP code: 5 minutes (300s)
- Access token: 15 minutes (900s)
- Refresh token: 7 days (604800s)

## Common Errors

- 400 if identifier is empty or OTP not requested
- 400 if OTP expired (5 minutes passed)
- 401 if OTP code is incorrect
- 401 if access_token or refresh_token is invalid or expired
- 404 if user not found after token validation

## Notes

- User is auto-created on first OTP verification
- For testing only: OTP code is returned in POST /auth/request-otp response
