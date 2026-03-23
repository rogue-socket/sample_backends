---
name: OTP Auth Server
description: Passwordless authentication via OTP codes with session token lifecycle.
port: 8004
tech: FastAPI
---

# OTP Auth Server Skill

FastAPI-based passwordless authentication service running on port 8004. Provides OTP (One-Time Password) based login with access/refresh token sessions.

## Overview

**Purpose:** Implement secure passwordless authentication using time-limited OTP codes. Issues short-lived access tokens (15 min) and long-lived refresh tokens (7 days) for session management.

**When to Use:**
- Building passwordless login flows
- Testing authentication workflows without passwords
- Implementing OTP-based verification
- Testing token refresh and session lifecycle

**Base URL:** http://localhost:8004

**Default User:** Automatically created on first OTP verification

## Setup Verification

```bash
# Check service is running
curl -s http://localhost:8004/health | jq '.'

# Expected:
# {"status": "healthy"}
```

## Core Workflows with Examples

### 1. Request OTP Code

**Request:**
```bash
curl -X POST http://localhost:8004/auth/request-otp \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "alice@example.com"
  }'
```

**Response:**
```json
{
  "status": "success",
  "message": "OTP sent to alice@example.com",
  "user_id": "alice@example.com",
  "expires_in_seconds": 300
}
```

**Important:** In test mode, OTP is printed to server logs. Check server output for actual code.

### 2. Verify OTP and Get Tokens

**Request:**
```bash
curl -X POST http://localhost:8004/auth/verify-otp \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "alice@example.com",
    "otp_code": "123456"
  }'
```

**Response (Success):**
```json
{
  "status": "success",
  "message": "Authentication successful",
  "user_id": "alice@example.com",
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "access_token_expires_in_seconds": 900,
  "refresh_token_expires_in_seconds": 604800
}
```

**Response (Invalid OTP):**
```json
{
  "status": "failed",
  "message": "Invalid or expired OTP code",
  "user_id": "alice@example.com"
}
```

### 3. Use Access Token

**Request (with access token in header):**
```bash
curl -X POST http://localhost:8004/auth/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Response:**
```json
{
  "status": "success",
  "message": "Token is valid",
  "user_id": "alice@example.com",
  "token_type": "access",
  "expires_at": "2026-03-24T10:45:00Z"
}
```

### 4. Refresh Access Token (Key Workflow)

**When access token expires (15 min), use refresh token to get new one:**

**Request:**
```bash
curl -X POST http://localhost:8004/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }'
```

**Response:**
```json
{
  "status": "success",
  "message": "Token refreshed successfully",
  "user_id": "alice@example.com",
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "access_token_expires_in_seconds": 900
}
```

### 5. Logout

**Request:**
```bash
curl -X POST http://localhost:8004/auth/logout \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Response:**
```json
{
  "status": "success",
  "message": "Logged out successfully",
  "user_id": "alice@example.com"
}
```

## Token Lifetime Reference

| Token Type | Duration | Use Case | Refresh Allowed |
| --- | --- | --- | --- |
| Access Token | 15 minutes | API requests | No |
| Refresh Token | 7 days | Get new access token | Yes |
| OTP Code | 5 minutes | Verify identity | No (request new) |

## Common Issues and Troubleshooting

### Issue: OTP request returns 400
**Symptom:** `{"status": "failed", "message": "Invalid email format"}`

**Cause:** user_id looks like email but was rejected.

**Solution:** Verify user_id is properly formatted.

```bash
# Valid formats
curl -X POST http://localhost:8004/auth/request-otp \
  -H "Content-Type: application/json" \
  -d '{"user_id": "alice@example.com"}'

# Also works
curl -X POST http://localhost:8004/auth/request-otp \
  -H "Content-Type: application/json" \
  -d '{"user_id": "alice"}'
```

### Issue: "Invalid or expired OTP"
**Symptom:** Fresh OTP code returns verification error.

**Cause:** OTP expired (5 minute TTL) or wrong code entered.

**Solution:** Request new OTP code and verify immediately. Check server logs for actual code.

```bash
# Request OTP
curl -X POST http://localhost:8004/auth/request-otp \
  -H "Content-Type: application/json" \
  -d '{"user_id": "alice@example.com"}'

# Check server logs for OTP (in dev mode)
# Then verify within 5 minutes
```

### Issue: Access token rejected with 401
**Symptom:** `{"detail": "Invalid authentication credentials"}`

**Cause:** Token missing, malformed, expired, or invalid.

**Solution:** Verify token format and if expired, refresh it.

```bash
# Correct format
curl http://localhost:8004/auth/me \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

# NOT: Authorization: eyJ... (missing Bearer)
# If expired, refresh:
curl -X POST http://localhost:8004/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{"refresh_token": "..."}'
```

### Issue: Refresh token rejected
**Symptom:** `{"status": "failed", "message": "Invalid refresh token"}`

**Cause:** Refresh token expired (7 days) or malformed.

**Solution:** Request new OTP and restart authentication flow.

```bash
# Restart auth flow
curl -X POST http://localhost:8004/auth/request-otp \
  -H "Content-Type: application/json" \
  -d '{"user_id": "alice@example.com"}'
```

## Authentication Flow Diagram

```
User provides email
         ↓
Request OTP → OTP sent (5 min TTL)
         ↓
User receives OTP (check server logs)
         ↓
Verify OTP → Access token (15 min)
         + Refresh token (7 days)
         ↓
Use access_token in Authorization: Bearer header
         ↓
    [Token expires?]
      /          \\
    No            Yes
    │              │
    │              ▼
    │   Refresh with refresh_token
    │   → New access_token
    │              │
    │       ┌──────┘
    │       ▼
    └─→ Make API calls
```

## Integration Example: Complete Auth Flow

```bash
#!/bin/bash

user_id="alice@example.com"

echo "Step 1: Request OTP"
curl -s -X POST http://localhost:8004/auth/request-otp \
  -H "Content-Type: application/json" \
  -d "{\"user_id\": \"$user_id\"}" | jq '.'

echo "Step 2: Check server logs for OTP code"
echo "Using example OTP: 123456"

echo "Step 3: Verify OTP"
auth_response=$(curl -s -X POST http://localhost:8004/auth/verify-otp \
  -H "Content-Type: application/json" \
  -d "{\"user_id\": \"$user_id\", \"otp_code\": \"123456\"}")

access_token=$(echo $auth_response | jq -r '.access_token')
refresh_token=$(echo $auth_response | jq -r '.refresh_token')

echo "Access token: ${access_token:0:50}..."
echo "Refresh token: ${refresh_token:0:50}..."

echo "Step 4: Validate access token"
curl -s http://localhost:8004/auth/me \
  -H "Authorization: Bearer $access_token" | jq '.'
```

## Endpoint Reference

| Method | Endpoint | Purpose | Auth Required |
| --- | --- | --- | --- |
| GET | /health | Health check | No |
| POST | /auth/request-otp | Begin auth, send OTP | No |
| POST | /auth/verify-otp | Submit OTP, get tokens | No |
| POST | /auth/refresh | Get new access token | No (refresh_token) |
| POST | /auth/me | Validate access token | Yes (access_token) |
| POST | /auth/logout | Invalidate session | Yes (access_token) |

## Related Services

- All other servers (store, payments, file_upload, search, messaging) can integrate this for authenticated endpoints
- Could integrate with messaging_server to require auth before joining chat rooms

- 400 if identifier is empty or OTP not requested
- 400 if OTP expired (5 minutes passed)
- 401 if OTP code is incorrect
- 401 if access_token or refresh_token is invalid or expired
- 404 if user not found after token validation

## Notes

- User is auto-created on first OTP verification
- For testing only: OTP code is returned in POST /auth/request-otp response
