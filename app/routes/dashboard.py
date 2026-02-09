from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.idea import Idea
from app.models.task import Task

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/stats")
def stats(db: Session = Depends(get_db)):
    total_ideas = db.query(Idea).count()
    total_tasks = db.query(Task).count()
    done_tasks = db.query(Task).filter(Task.status == "done").count()

    return {
        "total_ideas": total_ideas,
        "total_tasks": total_tasks,
        "completed_tasks": done_tasks,
    }