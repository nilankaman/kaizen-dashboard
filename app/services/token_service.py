from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from jose import jwt

from app.core.config import settings
from app.models.refresh_token import RefreshToken


def issue_refresh(db: Session, user_id: int) -> str:
    """Create and store a refresh token."""
    now = datetime.now(timezone.utc)
    exp = now + timedelta(days=settings.jwt_refresh_ttl_days)

    token_str = jwt.encode(
        {"sub": str(user_id), "type": "refresh", "iat": int(now.timestamp()), "exp": exp},
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm
    )

    db_token = RefreshToken(
        user_id=user_id,
        token=token_str,
        expires_at=exp
    )
    db.add(db_token)
    db.commit()
    return token_str


def revoke_refresh(db: Session, token: str):
    """Delete refresh token from database."""
    db.query(RefreshToken).filter(RefreshToken.token == token).delete()
    db.commit()


def is_refresh_valid(db: Session, token: str) -> bool:
    """Check if refresh token is valid and not expired."""
    rec = db.query(RefreshToken).filter(RefreshToken.token == token).first()
    if not rec:
        return False
    if rec.expires_at < datetime.now(timezone.utc):
        return False
    return True