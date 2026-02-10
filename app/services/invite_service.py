from datetime import datetime, timedelta, timezone
from jose import jwt

from app.core.config import settings


def create_invite_token(invite_id: int, team_id: int, email: str) -> str:
    now = datetime.now(timezone.utc)
    exp = now + timedelta(minutes=settings.invite_ttl_min)

    payload = {
        "type": "team_invite",
        "invite_id": invite_id,
        "team_id": team_id,
        "email": email,
        "iat": int(now.timestamp()),
        "exp": exp,
    }
    return jwt.encode(payload, settings.invite_secret_key, algorithm=settings.jwt_algorithm)


def decode_invite_token(token: str) -> dict:
    payload = jwt.decode(token, settings.invite_secret_key, algorithms=[settings.jwt_algorithm])

    if payload.get("type") != "team_invite":
        raise ValueError("Invalid invite token type")

    return payload