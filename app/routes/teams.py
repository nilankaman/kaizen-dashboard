from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from app.db.session import get_db
from app.core.errors import api_error
from app.core.security import hash_password

from app.models.team import Team
from app.models.user import User
from app.models.team_member import TeamMember
from app.models.team_invite import TeamInvite
from app.models.audit_log import AuditLog

from app.schemas.invite import TeamInviteCreate, TeamInviteOut, AcceptInviteRequest
from app.services.invite_service import create_invite_token, decode_invite_token
from app.services.email_service import send_invite_email
from app.core.config import settings

router = APIRouter(prefix="/teams", tags=["teams"])


@router.get("/")
def list_teams(db: Session = Depends(get_db)):
    teams = db.query(Team).all()
    return [{"id": t.id, "name": t.name, "description": getattr(t, "description", None)} for t in teams]


@router.post("/{team_id}/invite", response_model=TeamInviteOut)
def invite_member(team_id: int, payload: TeamInviteCreate, db: Session = Depends(get_db)):
    inviter_user_id = 1  # TODO: Replace with authenticated user

    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        api_error(404, "TEAM_NOT_FOUND", "Team not found.")

    token, exp = create_invite_token(team_id, str(payload.email), payload.role)

    invite = TeamInvite(
        team_id=team_id,
        email=str(payload.email),
        role=payload.role,
        token=token,
        expires_at=exp,
        created_by=inviter_user_id,
    )
    db.add(invite)

    db.add(AuditLog(
        action="TEAM_INVITE_CREATED",
        entity="team_invite",
        entity_id=0,
        performed_by=inviter_user_id,
    ))

    db.commit()

    invite_link = f"{settings.app_base_url}/docs#/teams/accept_invite?token={token}"
    send_invite_email(str(payload.email), invite_link)

    return {
        "team_id": team_id,
        "email": payload.email,
        "role": payload.role,
        "expires_at": exp.isoformat(),
    }


@router.post("/accept-invite")
def accept_invite(payload: AcceptInviteRequest, db: Session = Depends(get_db)):
    try:
        data = decode_invite_token(payload.token)
    except Exception:
        api_error(400, "INVITE_TOKEN_INVALID", "Invalid or expired token.")

    if data.get("type") != "team_invite":
        api_error(400, "INVITE_TOKEN_INVALID", "Invalid token.")

    team_id = int(data["team_id"])
    email = str(data["email"]).lower()
    role = str(data.get("role", "member"))

    invite = db.query(TeamInvite).filter(TeamInvite.token == payload.token).first()
    if not invite:
        api_error(400, "INVITE_NOT_FOUND", "Invite not found.")
    if invite.accepted:
        api_error(400, "INVITE_ALREADY_USED", "Invite already used.")
    if invite.expires_at < datetime.now(timezone.utc):
        api_error(400, "INVITE_EXPIRED", "Invite expired.")

    user = db.query(User).filter(User.email == email).first()
    if not user:
        user = User(
            email=email,
            name=payload.name,
            password_hash=hash_password(payload.password),
            role="member",
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    exists = db.query(TeamMember).filter(
        TeamMember.team_id == team_id,
        TeamMember.user_id == user.id
    ).first()

    if not exists:
        db.add(TeamMember(team_id=team_id, user_id=user.id, role=role))

    invite.accepted = True
    invite.accepted_at = datetime.now(timezone.utc)

    db.add(AuditLog(
        action="TEAM_INVITE_ACCEPTED",
        entity="team_invite",
        entity_id=invite.id,
        performed_by=user.id,
    ))

    db.commit()

    return {
        "status": "accepted",
        "team_id": team_id,
        "user_id": user.id,
        "email": user.email,
        "role": role,
    }
