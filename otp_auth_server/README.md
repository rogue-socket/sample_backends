# OTP Auth Server

FastAPI server for OTP-based mock authentication with access and refresh sessions.

## Run

```bash
pip install -r requirements.txt
python -m uvicorn main:app --reload --port 8004
```

Docs: http://localhost:8004/docs

## Health

- GET /health

## Key Endpoints

| Method | Endpoint | Description |
| --- | --- | --- |
| POST | /auth/request-otp | Request OTP for email/phone identifier |
| POST | /auth/verify-otp | Verify OTP and create session tokens |
| POST | /auth/refresh | Rotate refresh token and issue new tokens |
| POST | /auth/me | Resolve user by access token |
| POST | /auth/logout | Revoke refresh token and related access tokens |
| POST | /auth/reset | Reset all in-memory auth state |

## Quick Example

```bash
curl -X POST http://localhost:8004/auth/request-otp \
  -H "Content-Type: application/json" \
  -d '{"identifier":"alice@example.com"}'
```

## Notes

- OTP codes are returned in response for local testing only.
- All data is in-memory and resets on restart.
