from typing import Literal
from pydantic import BaseModel, Field


class TaskCreate(BaseModel):
    title: str = Field(min_length=3, max_length=80)
    description: str | None = None
    status: Literal["todo", "in_progress", "done"] = "todo"
    priority: int = Field(ge=1, le=5)


class TaskResponse(BaseModel):
    id: int
    title: str
    description: str | None
    status: str
    priority: int
    owner_id: int


class TaskStatusUpdate(BaseModel):
    status: Literal["todo", "in_progress", "done"]


class CurrentUser(BaseModel):
    id: int
    role: str = "user"
