from datetime import UTC, datetime, timedelta
import secrets
import uuid

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="OTP Auth Server")

OTP_TTL_SECONDS = 300
ACCESS_TTL_SECONDS = 900
REFRESH_TTL_SECONDS = 7 * 24 * 3600

# In-memory stores
USERS: dict[str, dict] = {}
OTP_CODES: dict[str, dict] = {}
ACCESS_SESSIONS: dict[str, dict] = {}
REFRESH_SESSIONS: dict[str, dict] = {}


class OtpRequest(BaseModel):
    identifier: str = Field(min_length=3, description="Email or phone")


class OtpVerify(BaseModel):
    identifier: str = Field(min_length=3)
    otp_code: str = Field(min_length=4, max_length=8)


class RefreshRequest(BaseModel):
    refresh_token: str


class LogoutRequest(BaseModel):
    refresh_token: str | None = None


class MeRequest(BaseModel):
    access_token: str


def utc_now() -> datetime:
    return datetime.now(UTC)


def to_iso(value: datetime) -> str:
    return value.isoformat()


def create_user_if_missing(identifier: str) -> dict:
    user = USERS.get(identifier)
    if user is None:
        user = {
            "user_id": uuid.uuid4().hex,
            "identifier": identifier,
            "created_at": to_iso(utc_now()),
        }
        USERS[identifier] = user
    return user


def generate_otp() -> str:
    return f"{secrets.randbelow(1000000):06d}"


def create_session_tokens(identifier: str) -> dict:
    access_token = uuid.uuid4().hex
    refresh_token = uuid.uuid4().hex

    access_expires_at = utc_now() + timedelta(seconds=ACCESS_TTL_SECONDS)
    refresh_expires_at = utc_now() + timedelta(seconds=REFRESH_TTL_SECONDS)

    ACCESS_SESSIONS[access_token] = {
        "identifier": identifier,
        "expires_at": access_expires_at,
    }
    REFRESH_SESSIONS[refresh_token] = {
        "identifier": identifier,
        "expires_at": refresh_expires_at,
    }

    return {
        "access_token": access_token,
        "access_expires_at": to_iso(access_expires_at),
        "refresh_token": refresh_token,
        "refresh_expires_at": to_iso(refresh_expires_at),
    }


def get_valid_access_session(access_token: str) -> dict:
    session = ACCESS_SESSIONS.get(access_token)
    if session is None:
        raise HTTPException(status_code=401, detail="Invalid access token")

    if utc_now() > session["expires_at"]:
        ACCESS_SESSIONS.pop(access_token, None)
        raise HTTPException(status_code=401, detail="Access token expired")

    return session


def get_valid_refresh_session(refresh_token: str) -> dict:
    session = REFRESH_SESSIONS.get(refresh_token)
    if session is None:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    if utc_now() > session["expires_at"]:
        REFRESH_SESSIONS.pop(refresh_token, None)
        raise HTTPException(status_code=401, detail="Refresh token expired")

    return session


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "otp_auth"}


@app.post("/auth/request-otp")
def request_otp(payload: OtpRequest):
    identifier = payload.identifier.strip().lower()
    if not identifier:
        raise HTTPException(status_code=400, detail="identifier is required")

    create_user_if_missing(identifier)

    otp_code = generate_otp()
    expires_at = utc_now() + timedelta(seconds=OTP_TTL_SECONDS)
    OTP_CODES[identifier] = {
        "otp_code": otp_code,
        "expires_at": expires_at,
    }

    # For sample/testing only: return otp code directly.
    return {
        "status": "otp_sent",
        "identifier": identifier,
        "otp_code": otp_code,
        "expires_at": to_iso(expires_at),
    }


@app.post("/auth/verify-otp")
def verify_otp(payload: OtpVerify):
    identifier = payload.identifier.strip().lower()
    stored = OTP_CODES.get(identifier)

    if stored is None:
        raise HTTPException(status_code=400, detail="No OTP requested for identifier")

    if utc_now() > stored["expires_at"]:
        OTP_CODES.pop(identifier, None)
        raise HTTPException(status_code=400, detail="OTP expired")

    if payload.otp_code != stored["otp_code"]:
        raise HTTPException(status_code=401, detail="Invalid OTP code")

    OTP_CODES.pop(identifier, None)
    user = create_user_if_missing(identifier)
    tokens = create_session_tokens(identifier)

    return {
        "status": "authenticated",
        "user": user,
        **tokens,
    }


@app.post("/auth/refresh")
def refresh_session(payload: RefreshRequest):
    refresh_session_data = get_valid_refresh_session(payload.refresh_token)
    identifier = refresh_session_data["identifier"]

    REFRESH_SESSIONS.pop(payload.refresh_token, None)
    tokens = create_session_tokens(identifier)

    return {
        "status": "refreshed",
        **tokens,
    }


@app.post("/auth/logout")
def logout(payload: LogoutRequest):
    revoked_refresh = False
    revoked_access = 0

    if payload.refresh_token:
        session = REFRESH_SESSIONS.pop(payload.refresh_token, None)
        if session is not None:
            revoked_refresh = True
            identifier = session["identifier"]
            to_remove = [
                token
                for token, access_session in ACCESS_SESSIONS.items()
                if access_session["identifier"] == identifier
            ]
            for token in to_remove:
                ACCESS_SESSIONS.pop(token, None)
                revoked_access += 1

    return {
        "status": "logged_out",
        "revoked_refresh": revoked_refresh,
        "revoked_access_tokens": revoked_access,
    }


@app.post("/auth/me")
def get_me(payload: MeRequest):
    session = get_valid_access_session(payload.access_token)
    user = USERS.get(session["identifier"])
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "user": user,
        "access_expires_at": to_iso(session["expires_at"]),
    }


@app.post("/auth/reset")
def reset_state():
    USERS.clear()
    OTP_CODES.clear()
    ACCESS_SESSIONS.clear()
    REFRESH_SESSIONS.clear()
    return {"status": "reset"}
