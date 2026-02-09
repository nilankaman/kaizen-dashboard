from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse
from app.core.security import hash_password, verify_password, create_access_token, decode_token
from app.core.errors import api_error
from app.models.user import User
from app.services.token_service import issue_refresh, revoke_refresh, is_refresh_valid

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == payload.email).first():
        api_error(409, "EMAIL_EXISTS", "Email already registered.")

    user = User(
        name=payload.name,
        email=payload.email,
        password_hash=hash_password(payload.password),
        role=payload.role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    access = create_access_token(user.id, user.role)
    refresh = issue_refresh(db, user.id)
    return TokenResponse(access_token=access, refresh_token=refresh)


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.password_hash):
        api_error(401, "INVALID_CREDENTIALS", "Invalid email or password.")

    access = create_access_token(user.id, user.role)
    refresh = issue_refresh(db, user.id)
    return TokenResponse(access_token=access, refresh_token=refresh)


@router.post("/refresh", response_model=TokenResponse)
def refresh(refresh_token: str, db: Session = Depends(get_db)):
    if not is_refresh_valid(db, refresh_token):
        api_error(401, "INVALID_REFRESH", "Invalid refresh token.")

    try:
        payload = decode_token(refresh_token)
        if payload.get("type") != "refresh":
            api_error(401, "INVALID_REFRESH", "Invalid refresh token.")
        user_id = int(payload["sub"])
    except Exception:
        api_error(401, "INVALID_REFRESH", "Invalid refresh token.")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        api_error(401, "USER_NOT_FOUND", "User not found.")

    revoke_refresh(db, refresh_token)
    new_refresh = issue_refresh(db, user.id)
    access = create_access_token(user.id, user.role)
    return TokenResponse(access_token=access, refresh_token=new_refresh)


@router.post("/logout")
def logout(refresh_token: str, db: Session = Depends(get_db)):
    revoke_refresh(db, refresh_token)
    return {"message": "logged out"}
