from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.idea import Idea
from app.models.user import User
from app.core.errors import api_error
from app.schemas.idea import IdeaCreate, IdeaUpdate, IdeaOut

router = APIRouter(prefix="/ideas", tags=["ideas"])


@router.post("/", response_model=IdeaOut)
def create_idea(payload: IdeaCreate, db: Session = Depends(get_db)):
    idea = Idea(
        title=payload.title,
        description=payload.description,
        team_id=payload.team_id,
        creator_id=1  # replace with current user later
    )
    db.add(idea)
    db.commit()
    db.refresh(idea)
    return idea


@router.get("/", response_model=list[IdeaOut])
def list_ideas(db: Session = Depends(get_db)):
    ideas = db.query(Idea).all()
    return ideas


@router.get("/{idea_id}", response_model=IdeaOut)
def get_idea(idea_id: int, db: Session = Depends(get_db)):
    idea = db.query(Idea).filter(Idea.id == idea_id).first()
    if not idea:
        api_error(404, "IDEA_NOT_FOUND", "Idea not found.")
    return idea


@router.patch("/{idea_id}", response_model=IdeaOut)
def update_idea(idea_id: int, payload: IdeaUpdate, db: Session = Depends(get_db)):
    idea = db.query(Idea).filter(Idea.id == idea_id).first()
    if not idea:
        api_error(404, "IDEA_NOT_FOUND", "Idea not found.")

    if payload.title is not None:
        idea.title = payload.title
    if payload.description is not None:
        idea.description = payload.description
    if payload.status is not None:
        idea.status = payload.status

    db.commit()
    db.refresh(idea)
    return idea