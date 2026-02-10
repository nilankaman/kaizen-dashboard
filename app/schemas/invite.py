from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


class TeamInviteCreate(BaseModel):
    email: EmailStr


class TeamInviteOut(BaseModel):
    id: int
    email: EmailStr
    team_id: int
    expires_at: datetime

    class Config:
        from_attributes = True


class AcceptInviteRequest(BaseModel):
    token: str = Field(..., min_length=10)
    name: str = Field(..., min_length=2, max_length=100)
    password: str = Field(..., min_length=6, max_length=72)