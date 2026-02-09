from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.core.errors import api_error

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=list[dict])
def list_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return [
        {"id": u.id, "name": u.name, "email": u.email, "role": u.role}
        for u in users
    ]


@router.get("/{user_id}", response_model=dict)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        api_error(404, "USER_NOT_FOUND", "User not found.")
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "role": user.role,
    }
