from pydantic import BaseModel

class IdeaCreate(BaseModel):
    title: str
    description: str
    team_id: int

class IdeaUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    status: str | None = None

class IdeaOut(BaseModel):
    id: int
    title: str
    description: str
    status: str
    team_id: int
    creator_id: int

    class Config:
        from_attributes = True