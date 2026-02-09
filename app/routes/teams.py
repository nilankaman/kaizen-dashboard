from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.team import Team
from app.core.errors import api_error

router = APIRouter(prefix="/teams", tags=["teams"])


@router.get("/", response_model=list[dict])
def list_teams(db: Session = Depends(get_db)):
    teams = db.query(Team).all()
    return [
        {"id": t.id, "name": t.name}
        for t in teams
    ]


@router.get("/{team_id}", response_model=dict)
def get_team(team_id: int, db: Session = Depends(get_db)):
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        api_error(404, "TEAM_NOT_FOUND", "Team not found.")
    return {"id": team.id, "name": team.name}